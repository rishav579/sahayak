export type User = {
  _id: string;
  google_id: string;
  email: string;
  name: string;
  picture?: string;
  created_at: string;
};

export type ActionItem = {
  _id: string;
  meeting_id: string;
  task: string;
  assignee?: string | null;
  deadline?: string | null;
  status: 'pending' | 'completed' | 'overdue';
  reminder_sent: boolean;
  created_at: string;
};

export type Meeting = {
  _id: string;
  user_id: string;
  title: string;
  audio_url?: string | null;
  transcript: string;
  action_items: ActionItem[];
  created_at: string;
};

export type AuthResponse = {
  access_token: string;
  token_type: string;
  user: User;
};
