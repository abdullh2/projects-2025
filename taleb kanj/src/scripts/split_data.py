import os
import shutil
import random

def split_data(train_dir, val_dir, val_split=0.2):
   
    os.makedirs(val_dir, exist_ok=True)
    
    
    train_images = [f for f in os.listdir(train_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
    
   
    num_val = int(len(train_images) * val_split)
    
  
    val_images = random.sample(train_images, num_val)
    
 
    for img_name in val_images:
       
        src_img = os.path.join(train_dir, img_name)
        dst_img = os.path.join(val_dir, img_name)
        shutil.move(src_img, dst_img)
        
      
        label_name = os.path.splitext(img_name)[0] + '.txt'
        src_label = os.path.join(train_dir.replace('images', 'labels'), label_name)
        dst_label = os.path.join(val_dir.replace('images', 'labels'), label_name)
    
        os.makedirs(os.path.dirname(dst_label), exist_ok=True)
        
        if os.path.exists(src_label):
            shutil.move(src_label, dst_label)

if __name__ == '__main__':
 
    train_dir = os.path.join('data', 'images', 'train')
    val_dir = os.path.join('data', 'images', 'val')
    
  
    split_data(train_dir, val_dir)
    print('Data split completed successfully!')