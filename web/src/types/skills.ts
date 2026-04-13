export interface SkillInput {
  name: string;
  type: string;
  description: string;
  required: boolean;
  default?: unknown;
  enum?: string[];
}

export interface SkillOutput {
  type: string;
  description: string;
}

export interface Skill {
  name: string;
  description: string;
  version: string;
  inputs: SkillInput[];
  output: SkillOutput;
}

export interface SkillRunRequest {
  params: Record<string, unknown>;
}

export interface SkillRunResponse {
  success: boolean;
  output: string;
  error: string;
}
