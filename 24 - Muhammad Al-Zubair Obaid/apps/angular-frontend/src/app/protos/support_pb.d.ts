import * as jspb from 'google-protobuf'



export class InstallAppsRequest extends jspb.Message {
  getAppIdsList(): Array<string>;
  setAppIdsList(value: Array<string>): InstallAppsRequest;
  clearAppIdsList(): InstallAppsRequest;
  addAppIds(value: string, index?: number): InstallAppsRequest;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): InstallAppsRequest.AsObject;
  static toObject(includeInstance: boolean, msg: InstallAppsRequest): InstallAppsRequest.AsObject;
  static serializeBinaryToWriter(message: InstallAppsRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): InstallAppsRequest;
  static deserializeBinaryFromReader(message: InstallAppsRequest, reader: jspb.BinaryReader): InstallAppsRequest;
}

export namespace InstallAppsRequest {
  export type AsObject = {
    appIdsList: Array<string>,
  }
}

export class InstallEnvironmentRequest extends jspb.Message {
  getEnvironmentId(): string;
  setEnvironmentId(value: string): InstallEnvironmentRequest;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): InstallEnvironmentRequest.AsObject;
  static toObject(includeInstance: boolean, msg: InstallEnvironmentRequest): InstallEnvironmentRequest.AsObject;
  static serializeBinaryToWriter(message: InstallEnvironmentRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): InstallEnvironmentRequest;
  static deserializeBinaryFromReader(message: InstallEnvironmentRequest, reader: jspb.BinaryReader): InstallEnvironmentRequest;
}

export namespace InstallEnvironmentRequest {
  export type AsObject = {
    environmentId: string,
  }
}

export class QuerySystemInfoRequest extends jspb.Message {
  getIncludeDrivers(): boolean;
  setIncludeDrivers(value: boolean): QuerySystemInfoRequest;

  getIncludeGpuInfo(): boolean;
  setIncludeGpuInfo(value: boolean): QuerySystemInfoRequest;

  getIncludeStorageInfo(): boolean;
  setIncludeStorageInfo(value: boolean): QuerySystemInfoRequest;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): QuerySystemInfoRequest.AsObject;
  static toObject(includeInstance: boolean, msg: QuerySystemInfoRequest): QuerySystemInfoRequest.AsObject;
  static serializeBinaryToWriter(message: QuerySystemInfoRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): QuerySystemInfoRequest;
  static deserializeBinaryFromReader(message: QuerySystemInfoRequest, reader: jspb.BinaryReader): QuerySystemInfoRequest;
}

export namespace QuerySystemInfoRequest {
  export type AsObject = {
    includeDrivers: boolean,
    includeGpuInfo: boolean,
    includeStorageInfo: boolean,
  }
}

export class SystemInfoResponse extends jspb.Message {
  getCpuName(): string;
  setCpuName(value: string): SystemInfoResponse;

  getRamTotalGb(): string;
  setRamTotalGb(value: string): SystemInfoResponse;

  getGpuName(): string;
  setGpuName(value: string): SystemInfoResponse;

  getOsVersion(): string;
  setOsVersion(value: string): SystemInfoResponse;

  getStorageDevicesList(): Array<StorageDevice>;
  setStorageDevicesList(value: Array<StorageDevice>): SystemInfoResponse;
  clearStorageDevicesList(): SystemInfoResponse;
  addStorageDevices(value?: StorageDevice, index?: number): StorageDevice;

  getDriversList(): Array<DriverInfo>;
  setDriversList(value: Array<DriverInfo>): SystemInfoResponse;
  clearDriversList(): SystemInfoResponse;
  addDrivers(value?: DriverInfo, index?: number): DriverInfo;

  getError(): Error | undefined;
  setError(value?: Error): SystemInfoResponse;
  hasError(): boolean;
  clearError(): SystemInfoResponse;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): SystemInfoResponse.AsObject;
  static toObject(includeInstance: boolean, msg: SystemInfoResponse): SystemInfoResponse.AsObject;
  static serializeBinaryToWriter(message: SystemInfoResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): SystemInfoResponse;
  static deserializeBinaryFromReader(message: SystemInfoResponse, reader: jspb.BinaryReader): SystemInfoResponse;
}

export namespace SystemInfoResponse {
  export type AsObject = {
    cpuName: string,
    ramTotalGb: string,
    gpuName: string,
    osVersion: string,
    storageDevicesList: Array<StorageDevice.AsObject>,
    driversList: Array<DriverInfo.AsObject>,
    error?: Error.AsObject,
  }
}

export class StorageDevice extends jspb.Message {
  getModel(): string;
  setModel(value: string): StorageDevice;

  getSizeGb(): string;
  setSizeGb(value: string): StorageDevice;

  getFreeSpaceGb(): string;
  setFreeSpaceGb(value: string): StorageDevice;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): StorageDevice.AsObject;
  static toObject(includeInstance: boolean, msg: StorageDevice): StorageDevice.AsObject;
  static serializeBinaryToWriter(message: StorageDevice, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): StorageDevice;
  static deserializeBinaryFromReader(message: StorageDevice, reader: jspb.BinaryReader): StorageDevice;
}

export namespace StorageDevice {
  export type AsObject = {
    model: string,
    sizeGb: string,
    freeSpaceGb: string,
  }
}

export class DriverInfo extends jspb.Message {
  getDeviceName(): string;
  setDeviceName(value: string): DriverInfo;

  getDriverVersion(): string;
  setDriverVersion(value: string): DriverInfo;

  getStatus(): string;
  setStatus(value: string): DriverInfo;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): DriverInfo.AsObject;
  static toObject(includeInstance: boolean, msg: DriverInfo): DriverInfo.AsObject;
  static serializeBinaryToWriter(message: DriverInfo, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): DriverInfo;
  static deserializeBinaryFromReader(message: DriverInfo, reader: jspb.BinaryReader): DriverInfo;
}

export namespace DriverInfo {
  export type AsObject = {
    deviceName: string,
    driverVersion: string,
    status: string,
  }
}

export class RunCommandRequest extends jspb.Message {
  getCommand(): string;
  setCommand(value: string): RunCommandRequest;

  getArgsList(): Array<string>;
  setArgsList(value: Array<string>): RunCommandRequest;
  clearArgsList(): RunCommandRequest;
  addArgs(value: string, index?: number): RunCommandRequest;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): RunCommandRequest.AsObject;
  static toObject(includeInstance: boolean, msg: RunCommandRequest): RunCommandRequest.AsObject;
  static serializeBinaryToWriter(message: RunCommandRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): RunCommandRequest;
  static deserializeBinaryFromReader(message: RunCommandRequest, reader: jspb.BinaryReader): RunCommandRequest;
}

export namespace RunCommandRequest {
  export type AsObject = {
    command: string,
    argsList: Array<string>,
  }
}

export class RunCommandResponse extends jspb.Message {
  getStandardOutput(): string;
  setStandardOutput(value: string): RunCommandResponse;

  getStandardError(): string;
  setStandardError(value: string): RunCommandResponse;

  getExitCode(): number;
  setExitCode(value: number): RunCommandResponse;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): RunCommandResponse.AsObject;
  static toObject(includeInstance: boolean, msg: RunCommandResponse): RunCommandResponse.AsObject;
  static serializeBinaryToWriter(message: RunCommandResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): RunCommandResponse;
  static deserializeBinaryFromReader(message: RunCommandResponse, reader: jspb.BinaryReader): RunCommandResponse;
}

export namespace RunCommandResponse {
  export type AsObject = {
    standardOutput: string,
    standardError: string,
    exitCode: number,
  }
}

export class ProgressUpdate extends jspb.Message {
  getCurrentTask(): string;
  setCurrentTask(value: string): ProgressUpdate;

  getOverallPercentage(): number;
  setOverallPercentage(value: number): ProgressUpdate;

  getStatus(): ProgressUpdate.Status;
  setStatus(value: ProgressUpdate.Status): ProgressUpdate;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ProgressUpdate.AsObject;
  static toObject(includeInstance: boolean, msg: ProgressUpdate): ProgressUpdate.AsObject;
  static serializeBinaryToWriter(message: ProgressUpdate, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ProgressUpdate;
  static deserializeBinaryFromReader(message: ProgressUpdate, reader: jspb.BinaryReader): ProgressUpdate;
}

export namespace ProgressUpdate {
  export type AsObject = {
    currentTask: string,
    overallPercentage: number,
    status: ProgressUpdate.Status,
  }

  export enum Status { 
    UNKNOWN = 0,
    IN_PROGRESS = 1,
    COMPLETED = 2,
    FAILED = 3,
  }
}

export class Error extends jspb.Message {
  getCode(): string;
  setCode(value: string): Error;

  getMessage(): string;
  setMessage(value: string): Error;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): Error.AsObject;
  static toObject(includeInstance: boolean, msg: Error): Error.AsObject;
  static serializeBinaryToWriter(message: Error, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): Error;
  static deserializeBinaryFromReader(message: Error, reader: jspb.BinaryReader): Error;
}

export namespace Error {
  export type AsObject = {
    code: string,
    message: string,
  }
}

