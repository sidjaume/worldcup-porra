export type ID = string;

export type ApiErrorBody = {
  error?: {
    code?: string;
    message?: string;
    details?: Record<string, unknown>;
  };
  detail?: string;
};

export type User = {
  id: ID;
  email: string;
  display_name: string;
  avatar_url: string | null;
};

export type AuthTokenResponse = {
  access_token: string;
  refresh_token: string;
  token_type: "bearer";
  expires_in: number;
};

export type AuthExchangeResponse = AuthTokenResponse & {
  user: User;
};

export type PoolSummary = {
  id: ID;
  name: string;
  tournament_id: ID;
  role: "owner" | "participant";
  participant_count: number;
  created_at: string;
};

export type PoolDetail = {
  id: ID;
  name: string;
  tournament_id: ID;
  owner_user_id: ID;
  participant_count: number;
  created_at: string;
  is_active: boolean;
};

export type CreatePoolResponse = {
  id: ID;
  name: string;
  tournament_id: ID;
  role: "owner" | "participant";
  invite_code: string;
};

export type JoinPoolResponse = {
  pool_id: ID;
  name: string;
  role: "participant";
};

export type InviteCodeResponse = {
  invite_code: string;
  rotated_at: string;
};

export type Participant = {
  user_id: ID;
  display_name: string;
  role: "owner" | "participant";
  joined_at: string;
};

export type Tournament = {
  id: ID;
  name: string;
  year: number;
  is_active: boolean;
};

export type TeamBrief = {
  id: ID;
  name: string;
};

export type Team = TeamBrief & {
  short_name: string | null;
  fifa_code: string | null;
  flag_url: string | null;
};

export type TournamentStage =
  | "round_of_32"
  | "round_of_16"
  | "quarter_final"
  | "semi_final"
  | "final";

export type MatchStatus = "scheduled" | "completed" | "cancelled";

export type Match = {
  id: ID;
  stage: TournamentStage;
  bracket_position: number;
  home_team: TeamBrief | null;
  away_team: TeamBrief | null;
  scheduled_at: string;
  status: MatchStatus;
  home_score: number | null;
  away_score: number | null;
  winner_team_id: ID | null;
};

export type Prediction = {
  id: ID;
  match_id: ID;
  predicted_home_goals: number;
  predicted_away_goals: number;
  status: "editable" | "locked" | "scored";
  submitted_at: string;
  updated_at: string;
  score: PredictionScore | null;
};

export type PredictionScore = {
  points: number;
  correct_winner?: boolean;
  exact_score?: boolean;
};

export type PredictionWriteResponse = {
  id: ID;
  pool_id: ID;
  match_id: ID;
  predicted_home_goals: number;
  predicted_away_goals: number;
  status: "editable" | "locked" | "scored";
  submitted_at: string;
  updated_at: string;
};

export type VisiblePrediction = {
  user_id: ID;
  display_name: string;
  predicted_home_goals: number;
  predicted_away_goals: number;
  submitted_at: string;
  score: PredictionScore | null;
};

export type RankingRow = {
  rank: number;
  user_id: ID;
  display_name: string;
  total_points: number;
  exact_scores: number;
  correct_winners: number;
  predictions_scored: number;
  predictions_submitted: number;
};
