export type NotificationType = "success" | "info" | "warning" | "error";

export interface IMessage {
  id?: string;
  role: "user" | "assistant";
  content: string;
  user_id?: string;
  timestamp?: string;
  personalize?: boolean;
  ra?: string;
  session_id?: string;
  agency_id?: string;
}

export interface IStatus {
  message: string;
  status: boolean;
  data?: any;
}

export interface IChatMessage {
  text: string;
  sender: "user" | "assistant";
  metadata?: any;
  id?: string;
}

export interface IAgentConfig {
  name: string;
  system_message: string | "";
  code_execution_config?: boolean | string | { [key: string]: any } | null;
}

export interface IAgentFlowSpec {
  type: "assistant" | "userproxy" | "groupchat";
  config: IAgentConfig;
  timestamp?: string;
  id?: string;
  skills?: Array<ISkill>;
  description?: string;
  user_id?: string;
}

export interface IGroupChatConfig {
  agents: Array<IAgentFlowSpec>;
  admin_name: string;
  messages: Array<any>;
  max_round: number;
  speaker_selection_method: "auto" | "round_robin" | "random";
  allow_repeat_speaker: boolean | Array<IAgentConfig>;
}

export interface IFlowConfig {
  name: string;
  description: string;
  flows: Array<{
    sender: IAgentFlowSpec;
    receiver?: IAgentFlowSpec;
  }>;
  type: "twoagents" | "groupchat";
  timestamp?: string;
  id?: string;
  user_id?: string;
}

export interface IModelConfig {
  model: string;
  api_key?: string;
  api_version?: string;
  base_url?: string;
  api_type?: string;
  user_id?: string;
  timestamp?: string;
  description?: string;
}

export interface IMetadataFile {
  name: string;
  path: string;
  extension: string;
  content: string;
  type: string;
}

export interface IChatSession {
  id: string;
  user_id: string;
  timestamp: string;
  flow_config: IFlowConfig;
}

export interface ISkill {
  title: string;
  file_name?: string;
  content: string;
  id?: string;
  timestamp?: string;
  description?: string;
  user_id?: string;
  approved?: boolean;
  version?: number;
}
