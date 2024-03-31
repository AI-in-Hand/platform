export type NotificationType = "success" | "info" | "warning" | "error";

export interface IMessage {
  user_id: string;
  root_msg_id: string;
  msg_id?: string;
  role: string;
  content: string;
  timestamp?: string;
  personalize?: boolean;
  ra?: string;
  session_id?: string;
}

export interface IStatus {
  message: string;
  status: boolean;
  data?: any;
}

export interface IChatMessage {
  text: string;
  sender: "user" | "bot";
  metadata?: any;
  msg_id: string;
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

export interface IGroupChatFlowSpec {
  type: "groupchat";
  config: IAgentConfig;
  groupchat_config: IGroupChatConfig;
  id?: string;
  timestamp?: string;
  user_id?: string;
  description?: string;
}

export interface IFlowConfig {
  name: string;
  description: string;
  sender: IAgentFlowSpec;
  receiver: IAgentFlowSpec | IGroupChatFlowSpec;
  type: "twoagents" | "groupchat";
  timestamp?: string;
  summary_method?: "none" | "last" | "llm";
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

export interface IGalleryItem {
  id: string;
  messages: Array<IMessage>;
  session: IChatSession;
  tags: Array<string>;
  timestamp: string;
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
