
from __future__ import annotations

import argparse
import collections
import random
import time
from pathlib import Path

import cv2
import ale_py

import gymnasium as gym
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

# ──────────────────────────────────────────────────────────────────────────────
# 1. Hyper‑parameters (تم تعديلها لتقليل زمن التدريب وحجم الذاكرة)
# ──────────────────────────────────────────────────────────────────────────────
ENV_ID = "ALE/Pong-v5"  # Gymnasium Atari environment
STACK_FRAMES = 4
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

GAMMA = 0.99
LR = 1e-4
BATCH_SIZE = 16               # تقليل حجم الباتش
MEMORY_CAPACITY = 20_000      # تقليل سعة الذاكرة
MIN_MEMORY_FOR_TRAIN = 2_000  # بدء التدريب مبكراً مع بيانات أقل
TARGET_UPDATE_FREQ = 5_000    # تحديث شبكة الهدف بشكل أسرع
MAX_FRAMES = 50_000           # تقليل زمن التدريب كثيراً
SAVE_EVERY = 10_000           # حفظ النموذج بشكل متكرر

EPS_START = 1.0
EPS_END = 0.05
EPS_DECAY_FRAMES = 500_000

RUN_NAME = f"dqn_pong_{int(time.time())}"  # checkpoint folder

# ──────────────────────────────────────────────────────────────────────────────
# 2. Utilities: Replay Buffer & Frame Processing
# ──────────────────────────────────────────────────────────────────────────────
class ReplayBuffer:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.memory = collections.deque(maxlen=capacity)

    def push(self, state: np.ndarray, action: int, reward: float, next_state: np.ndarray, done: bool):
        self.memory.append((state, action, reward, next_state, done))

    def sample(self, batch_size: int):
        batch = random.sample(self.memory, batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        return (np.array(states, dtype=np.float32),
                np.array(actions),
                np.array(rewards, dtype=np.float32),
                np.array(next_states, dtype=np.float32),
                np.array(dones, dtype=np.bool_))

    def __len__(self):
        return len(self.memory)

# Frame preprocessing: gray‑scale, crop, resize to 84×84
_CROP = slice(34, 194)  # remove score & floor

def preprocess_frame(frame: np.ndarray) -> np.ndarray:
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)  # gray
    frame = frame[_CROP, :]                         # crop
    frame = cv2.resize(frame, (84, 84), interpolation=cv2.INTER_AREA)
    return frame / 255.0  # normalize to 0‑1

# ──────────────────────────────────────────────────────────────────────────────
# 3. Neural Network
# ──────────────────────────────────────────────────────────────────────────────
class DQN(nn.Module):
    def __init__(self, in_channels: int, n_actions: int):
        super().__init__()
        self.conv1 = nn.Conv2d(in_channels, 32, kernel_size=8, stride=4)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=4, stride=2)
        self.conv3 = nn.Conv2d(64, 64, kernel_size=3, stride=1)
        self.fc1 = nn.Linear(7 * 7 * 64, 512)
        self.out = nn.Linear(512, n_actions)

    def forward(self, x):
        x = x / 1.0  # already 0‑1, keep for clarity
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = F.relu(self.conv3(x))
        x = x.view(x.size(0), -1)
        x = F.relu(self.fc1(x))
        return self.out(x)

# ──────────────────────────────────────────────────────────────────────────────
# 4. Epsilon‑greedy policy
# ──────────────────────────────────────────────────────────────────────────────

def epsilon_by_frame(frame_idx: int) -> float:
    eps = EPS_END + (EPS_START - EPS_END) * max(0, (EPS_DECAY_FRAMES - frame_idx)) / EPS_DECAY_FRAMES
    return eps

# ──────────────────────────────────────────────────────────────────────────────
# 5. Environment wrapper: skip & stack frames
# ──────────────────────────────────────────────────────────────────────────────
class AtariWrapper:
    """Minimal wrap: frame‑skip 4 & stack 4 processed frames."""

    def __init__(self, env_id: str):
        self.env = gym.make(env_id, frameskip=1, repeat_action_probability=0.0, render_mode="human")

        self.action_space = self.env.action_space
        self.obs_queue = collections.deque(maxlen=STACK_FRAMES)

    def reset(self):
        obs, info = self.env.reset()
        frame = preprocess_frame(obs)
        for _ in range(STACK_FRAMES):
            self.obs_queue.append(frame)
        return np.stack(self.obs_queue, axis=0), info

    def step(self, action: int):
        total_reward = 0.0
        done = truncated = False
        for _ in range(4):
            obs, reward, done, truncated, info = self.env.step(action)
            total_reward += reward
            if done or truncated:
                break
        frame = preprocess_frame(obs)
        self.obs_queue.append(frame)
        next_state = np.stack(self.obs_queue, axis=0)
        return next_state, total_reward, done, truncated, info

    def close(self):
        self.env.close()

# ──────────────────────────────────────────────────────────────────────────────
# 6. Training loop
# ──────────────────────────────────────────────────────────────────────────────

def train():
    env = AtariWrapper(ENV_ID)
    n_actions = env.action_space.n

    policy_net = DQN(STACK_FRAMES, n_actions).to(DEVICE)
    target_net = DQN(STACK_FRAMES, n_actions).to(DEVICE)
    target_net.load_state_dict(policy_net.state_dict())
    target_net.eval()

    optimizer = optim.Adam(policy_net.parameters(), lr=LR, eps=1e-4)
    memory = ReplayBuffer(MEMORY_CAPACITY)

    state, _ = env.reset()
    frame_idx = 0
    episode_reward = 0
    rewards_history = []

    # main loop
    while frame_idx < MAX_FRAMES:
        eps = epsilon_by_frame(frame_idx)
        if random.random() < eps:
            action = env.action_space.sample()
        else:
            with torch.no_grad():
                state_v = torch.tensor(state, dtype=torch.float32).unsqueeze(0).to(DEVICE)
                q_values = policy_net(state_v)
                action = int(torch.argmax(q_values).item())

        next_state, reward, done, truncated, _ = env.step(action)
        memory.push(state, action, reward, next_state, done or truncated)
        state = next_state
        episode_reward += reward
        frame_idx += 1

        # learn when enough samples
        if len(memory) > MIN_MEMORY_FOR_TRAIN:
            states, actions, rewards, next_states, dones = memory.sample(BATCH_SIZE)
            states_v = torch.tensor(states).to(DEVICE)
            actions_v = torch.tensor(actions).unsqueeze(1).to(DEVICE)
            rewards_v = torch.tensor(rewards).to(DEVICE)
            next_states_v = torch.tensor(next_states).to(DEVICE)
            dones_v = torch.tensor(dones).to(DEVICE)

            q_values = policy_net(states_v).gather(1, actions_v).squeeze(1)
            with torch.no_grad():
                next_q = target_net(next_states_v).max(1)[0]
                expected_q = rewards_v + GAMMA * next_q * (~dones_v)

            loss = F.smooth_l1_loss(q_values, expected_q)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        # update target network
        if frame_idx % TARGET_UPDATE_FREQ == 0:
            target_net.load_state_dict(policy_net.state_dict())

        # logging + checkpoint
        if done:
            rewards_history.append(episode_reward)
            print(f"Frame: {frame_idx:7d} | Episode reward: {episode_reward:5.1f} | Eps: {eps:.3f}")
            state, _ = env.reset()
            episode_reward = 0

        if frame_idx % SAVE_EVERY == 0 and frame_idx > 0:
            save_path = Path(RUN_NAME)
            save_path.mkdir(parents=True, exist_ok=True)
            ckpt = save_path / f"dqn_pong_{frame_idx//1000}k.pt"
            torch.save(policy_net.state_dict(), ckpt)
            print(f"Model saved to {ckpt}")

    env.close()

# ──────────────────────────────────────────────────────────────────────────────
# 7. Play / Evaluation loop
# ──────────────────────────────────────────────────────────────────────────────

def play(model_path: str | None = None, episodes: int = 5):
    env = AtariWrapper(ENV_ID)
   # env.env.render_mode = "human"  # enable display
    n_actions = env.action_space.n

    policy_net = DQN(STACK_FRAMES, n_actions).to(DEVICE)
    if model_path:
        policy_net.load_state_dict(torch.load(model_path, map_location=DEVICE))
    policy_net.eval()

    for ep in range(episodes):
        state, _ = env.reset()
        done = False
        total_reward = 0
        while not done:
            with torch.no_grad():
                state_v = torch.tensor(state, dtype=torch.float32).unsqueeze(0).to(DEVICE)
                action = int(torch.argmax(policy_net(state_v)).item())
            next_state, reward, done, _, _ = env.step(action)
            total_reward += reward
            state = next_state
        print(f"Episode {ep+1}: Reward = {total_reward}")
    env.close()

# ──────────────────────────────────────────────────────────────────────────────
# 8. CLI
# ──────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="DQN agent for Atari Pong")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--train", action="store_true", help="Train from scratch")
    group.add_argument("--play", metavar="MODEL", help="Play using a saved model")
    args = parser.parse_args()

    if args.train:
        train()
    else:
        play(args.play)


if __name__ == "__main__":
    main()
