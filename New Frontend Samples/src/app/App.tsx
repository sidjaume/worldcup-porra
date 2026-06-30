import { useState, useMemo } from "react";
import { Trophy, Calendar, Target, ChevronDown, Check, Lock, Globe, Users, Star } from "lucide-react";
import { ImageWithFallback } from "./components/figma/ImageWithFallback";
import logoImg from "../imports/fifa-world-cup-2026-logo.png";

// ─── Types ───────────────────────────────────────────────────────────────────

interface Team {
  name: string;
  flag: string;
  code: string;
}

interface Match {
  id: string;
  round: string;
  group?: string;
  date: string;
  time: string;
  teamA: Team;
  teamB: Team;
  result?: { a: number; b: number };
  venue: string;
  confederation: string;
}

interface Prediction {
  matchId: string;
  userId: string;
  scoreA: number;
  scoreB: number;
}

interface User {
  id: string;
  name: string;
  avatar: string;
  color: string;
}

// ─── Data ────────────────────────────────────────────────────────────────────

const USERS: User[] = [
  { id: "u1", name: "Carlos M.", avatar: "CM", color: "#12C353" },
  { id: "u2", name: "Laura P.", avatar: "LP", color: "#f59e0b" },
  { id: "u3", name: "Javi R.", avatar: "JR", color: "#3b82f6" },
  { id: "u4", name: "Ana G.", avatar: "AG", color: "#ef4444" },
  { id: "u5", name: "Marcos T.", avatar: "MT", color: "#8b5cf6" },
];

const MATCHES: Match[] = [
  // Jornada 1 — UEFA (played)
  {
    id: "m1", round: "Jornada 1", group: "UEFA Grupo A", confederation: "UEFA",
    date: "2025-03-21", time: "20:45",
    teamA: { name: "España", flag: "🇪🇸", code: "ESP" },
    teamB: { name: "Países Bajos", flag: "🇳🇱", code: "NED" },
    result: { a: 3, b: 0 }, venue: "Estadio de La Cartuja, Sevilla",
  },
  {
    id: "m2", round: "Jornada 1", group: "UEFA Grupo B", confederation: "UEFA",
    date: "2025-03-21", time: "20:45",
    teamA: { name: "Francia", flag: "🇫🇷", code: "FRA" },
    teamB: { name: "Ucrania", flag: "🇺🇦", code: "UKR" },
    result: { a: 2, b: 1 }, venue: "Stade de France, París",
  },
  {
    id: "m3", round: "Jornada 1", group: "CONMEBOL", confederation: "CONMEBOL",
    date: "2025-03-25", time: "00:30",
    teamA: { name: "Argentina", flag: "🇦🇷", code: "ARG" },
    teamB: { name: "Brasil", flag: "🇧🇷", code: "BRA" },
    result: { a: 1, b: 1 }, venue: "Monumental, Buenos Aires",
  },
  // Jornada 2 — upcoming
  {
    id: "m4", round: "Jornada 2", group: "UEFA Grupo A", confederation: "UEFA",
    date: "2025-06-06", time: "20:45",
    teamA: { name: "España", flag: "🇪🇸", code: "ESP" },
    teamB: { name: "Dinamarca", flag: "🇩🇰", code: "DEN" },
    venue: "Estadio Santiago Bernabéu, Madrid",
  },
  {
    id: "m5", round: "Jornada 2", group: "UEFA Grupo B", confederation: "UEFA",
    date: "2025-06-06", time: "20:45",
    teamA: { name: "Inglaterra", flag: "🏴󠁧󠁢󠁥󠁮󠁧󠁿", code: "ENG" },
    teamB: { name: "Portugal", flag: "🇵🇹", code: "POR" },
    venue: "Wembley Stadium, Londres",
  },
  {
    id: "m6", round: "Jornada 2", group: "UEFA Grupo C", confederation: "UEFA",
    date: "2025-06-07", time: "18:00",
    teamA: { name: "Alemania", flag: "🇩🇪", code: "GER" },
    teamB: { name: "Italia", flag: "🇮🇹", code: "ITA" },
    venue: "Allianz Arena, Múnich",
  },
  {
    id: "m7", round: "Jornada 2", group: "CONMEBOL", confederation: "CONMEBOL",
    date: "2025-06-10", time: "02:00",
    teamA: { name: "Brasil", flag: "🇧🇷", code: "BRA" },
    teamB: { name: "Uruguay", flag: "🇺🇾", code: "URU" },
    venue: "Maracanã, Río de Janeiro",
  },
  {
    id: "m8", round: "Jornada 2", group: "CONCACAF", confederation: "CONCACAF",
    date: "2025-06-08", time: "22:00",
    teamA: { name: "México", flag: "🇲🇽", code: "MEX" },
    teamB: { name: "Estados Unidos", flag: "🇺🇸", code: "USA" },
    venue: "Estadio Azteca, Ciudad de México",
  },
  {
    id: "m9", round: "Jornada 2", group: "UEFA Grupo D", confederation: "UEFA",
    date: "2025-06-09", time: "20:45",
    teamA: { name: "Bélgica", flag: "🇧🇪", code: "BEL" },
    teamB: { name: "Turquía", flag: "🇹🇷", code: "TUR" },
    venue: "Estadio Rey Balduino, Bruselas",
  },
];

const INITIAL_PREDICTIONS: Prediction[] = [
  // u1 predictions (played matches)
  { matchId: "m1", userId: "u1", scoreA: 2, scoreB: 0 },
  { matchId: "m2", userId: "u1", scoreA: 2, scoreB: 1 },
  { matchId: "m3", userId: "u1", scoreA: 1, scoreB: 0 },
  // u2
  { matchId: "m1", userId: "u2", scoreA: 3, scoreB: 0 },
  { matchId: "m2", userId: "u2", scoreA: 1, scoreB: 0 },
  { matchId: "m3", userId: "u2", scoreA: 2, scoreB: 2 },
  // u3
  { matchId: "m1", userId: "u3", scoreA: 1, scoreB: 1 },
  { matchId: "m2", userId: "u3", scoreA: 3, scoreB: 1 },
  { matchId: "m3", userId: "u3", scoreA: 0, scoreB: 1 },
  // u4
  { matchId: "m1", userId: "u4", scoreA: 2, scoreB: 0 },
  { matchId: "m2", userId: "u4", scoreA: 2, scoreB: 0 },
  { matchId: "m3", userId: "u4", scoreA: 1, scoreB: 1 },
  // u5
  { matchId: "m1", userId: "u5", scoreA: 0, scoreB: 1 },
  { matchId: "m2", userId: "u5", scoreA: 1, scoreB: 2 },
  { matchId: "m3", userId: "u5", scoreA: 2, scoreB: 1 },
];

// ─── Scoring ─────────────────────────────────────────────────────────────────

function getResultOutcome(a: number, b: number): "home" | "draw" | "away" {
  return a > b ? "home" : a < b ? "away" : "draw";
}

function calcPoints(pred: Prediction, match: Match): number {
  if (!match.result) return 0;
  const { a, b } = match.result;
  if (pred.scoreA === a && pred.scoreB === b) return 3;
  if (getResultOutcome(pred.scoreA, pred.scoreB) === getResultOutcome(a, b)) return 1;
  return 0;
}

function calcUserPoints(userId: string, preds: Prediction[], matches: Match[]): number {
  return preds
    .filter((p) => p.userId === userId)
    .reduce((sum, p) => {
      const match = matches.find((m) => m.id === p.matchId);
      return sum + (match ? calcPoints(p, match) : 0);
    }, 0);
}

// ─── Sub-components ───────────────────────────────────────────────────────────

function Avatar({ user, size = "md" }: { user: User; size?: "sm" | "md" | "lg" }) {
  const sizes = { sm: "w-7 h-7 text-xs", md: "w-9 h-9 text-sm", lg: "w-12 h-12 text-base" };
  return (
    <div
      className={`${sizes[size]} rounded-full flex items-center justify-center font-bold font-mono shrink-0`}
      style={{ backgroundColor: user.color + "22", color: user.color, border: `1.5px solid ${user.color}44` }}
    >
      {user.avatar}
    </div>
  );
}

function ScoreInput({
  value,
  onChange,
  locked,
}: {
  value: string;
  onChange: (v: string) => void;
  locked: boolean;
}) {
  return (
    <input
      type="number"
      min={0}
      max={20}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      disabled={locked}
      className="w-12 h-10 text-center text-lg font-bold bg-secondary border border-border rounded-lg text-foreground disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-primary/50 [appearance:textfield] [&::-webkit-inner-spin-button]:appearance-none"
    />
  );
}

function PointBadge({ points }: { points: number }) {
  const colors =
    points === 3
      ? "bg-primary/15 text-primary border-primary/30"
      : points === 1
      ? "bg-accent/15 text-accent border-accent/30"
      : "bg-muted text-muted-foreground border-border";
  return (
    <span className={`text-xs font-mono font-medium px-2 py-0.5 rounded-full border ${colors}`}>
      {points === 3 ? "✓ +3" : points === 1 ? "~ +1" : "✗ 0"}
    </span>
  );
}

// ─── Match Card ───────────────────────────────────────────────────────────────

function MatchCard({
  match,
  currentUser,
  predictions,
  onPredict,
}: {
  match: Match;
  currentUser: User;
  predictions: Prediction[];
  onPredict: (matchId: string, a: number, b: number) => void;
}) {
  const existing = predictions.find((p) => p.matchId === match.id && p.userId === currentUser.id);
  const [localA, setLocalA] = useState(existing?.scoreA?.toString() ?? "");
  const [localB, setLocalB] = useState(existing?.scoreB?.toString() ?? "");
  const [saved, setSaved] = useState(!!existing);
  const isPlayed = !!match.result;

  const handleSave = () => {
    const a = parseInt(localA);
    const b = parseInt(localB);
    if (isNaN(a) || isNaN(b)) return;
    onPredict(match.id, a, b);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const myPred = predictions.find((p) => p.matchId === match.id && p.userId === currentUser.id);
  const myPoints = myPred && match.result ? calcPoints(myPred, match) : null;

  const dateObj = new Date(match.date + "T12:00:00");
  const dateStr = dateObj.toLocaleDateString("es-ES", { weekday: "short", day: "numeric", month: "short" });

  return (
    <div
      className={`rounded-2xl border overflow-hidden transition-all ${
        isPlayed ? "border-border" : "border-border hover:border-primary/30"
      }`}
      style={{ background: "var(--card)" }}
    >
      {/* Header strip */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-border bg-muted/40">
        <span className="text-xs text-muted-foreground font-medium uppercase tracking-wide">
          {match.group ?? match.confederation}
        </span>
        <div className="flex items-center gap-2">
          <Calendar size={11} className="text-muted-foreground" />
          <span className="text-xs text-muted-foreground font-mono">
            {dateStr} · {match.time}
          </span>
          {isPlayed && (
            <span className="ml-1 text-xs bg-primary/15 text-primary border border-primary/25 px-1.5 py-0.5 rounded-full font-medium">
              Finalizado
            </span>
          )}
        </div>
      </div>

      {/* Teams + scores */}
      <div className="px-5 py-5">
        <div className="flex items-center gap-3">
          {/* Team A */}
          <div className="flex-1 flex flex-col items-center gap-2">
            <span className="text-3xl">{match.teamA.flag}</span>
            <span
              className="text-base font-bold text-center leading-tight"
              style={{ fontFamily: "'Barlow Condensed', sans-serif", letterSpacing: "0.02em" }}
            >
              {match.teamA.name}
            </span>
          </div>

          {/* Score / VS */}
          <div className="flex flex-col items-center gap-2 min-w-[80px]">
            {isPlayed ? (
              <div className="flex items-center gap-2">
                <span className="text-3xl font-black" style={{ fontFamily: "'Barlow Condensed', sans-serif" }}>
                  {match.result!.a}
                </span>
                <span className="text-xl text-muted-foreground font-light">—</span>
                <span className="text-3xl font-black" style={{ fontFamily: "'Barlow Condensed', sans-serif" }}>
                  {match.result!.b}
                </span>
              </div>
            ) : (
              <span
                className="text-sm font-bold text-muted-foreground"
                style={{ fontFamily: "'Barlow Condensed', sans-serif", letterSpacing: "0.1em" }}
              >
                VS
              </span>
            )}
            {!isPlayed && (
              <span className="text-xs text-muted-foreground font-mono">{match.time}</span>
            )}
          </div>

          {/* Team B */}
          <div className="flex-1 flex flex-col items-center gap-2">
            <span className="text-3xl">{match.teamB.flag}</span>
            <span
              className="text-base font-bold text-center leading-tight"
              style={{ fontFamily: "'Barlow Condensed', sans-serif", letterSpacing: "0.02em" }}
            >
              {match.teamB.name}
            </span>
          </div>
        </div>

        {/* Venue */}
        <p className="text-center text-xs text-muted-foreground mt-3">{match.venue}</p>
      </div>

      {/* Prediction row */}
      <div className="px-5 pb-5 border-t border-border pt-4">
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Target size={13} />
            <span>Tu porra</span>
          </div>
          {isPlayed ? (
            <div className="flex items-center gap-3">
              {myPred ? (
                <>
                  <span className="text-sm font-mono font-bold text-foreground">
                    {myPred.scoreA} — {myPred.scoreB}
                  </span>
                  {myPoints !== null && <PointBadge points={myPoints} />}
                </>
              ) : (
                <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                  <Lock size={11} />
                  <span>Sin porra</span>
                </div>
              )}
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <ScoreInput value={localA} onChange={setLocalA} locked={false} />
              <span className="text-muted-foreground font-light text-lg">—</span>
              <ScoreInput value={localB} onChange={setLocalB} locked={false} />
              <button
                onClick={handleSave}
                disabled={localA === "" || localB === ""}
                className={`ml-1 px-3 py-2 rounded-lg text-sm font-semibold transition-all disabled:opacity-40 disabled:cursor-not-allowed ${
                  saved
                    ? "bg-primary/20 text-primary"
                    : "bg-primary text-primary-foreground hover:brightness-110 active:scale-95"
                }`}
              >
                {saved ? <Check size={15} /> : "Guardar"}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ─── Predictions Panel (other users) ─────────────────────────────────────────

function AllPredictionsPanel({
  match,
  users,
  predictions,
}: {
  match: Match;
  users: User[];
  predictions: Prediction[];
}) {
  const [open, setOpen] = useState(false);
  const isPlayed = !!match.result;

  if (!isPlayed && !open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="w-full text-xs text-muted-foreground hover:text-foreground transition-colors py-1 flex items-center justify-center gap-1.5"
      >
        <Users size={11} />
        Ver porras del grupo
      </button>
    );
  }

  const preds = users
    .map((u) => ({ user: u, pred: predictions.find((p) => p.matchId === match.id && p.userId === u.id) }))
    .filter((x) => x.pred);

  if (preds.length === 0) return null;

  return (
    <div className="px-5 pb-4 border-t border-border pt-4">
      <p className="text-xs text-muted-foreground mb-3 flex items-center gap-1.5">
        <Users size={11} />
        Porras del grupo
      </p>
      <div className="flex flex-wrap gap-2">
        {preds.map(({ user, pred }) => {
          const pts = pred && match.result ? calcPoints(pred, match) : null;
          return (
            <div
              key={user.id}
              className="flex items-center gap-2 bg-secondary rounded-xl px-3 py-1.5"
            >
              <Avatar user={user} size="sm" />
              <span className="text-xs font-medium">{user.name.split(" ")[0]}</span>
              {pred && (
                <span className="text-xs font-mono text-muted-foreground">
                  {pred.scoreA}–{pred.scoreB}
                </span>
              )}
              {pts !== null && <PointBadge points={pts} />}
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ─── Leaderboard ──────────────────────────────────────────────────────────────

function Leaderboard({
  users,
  predictions,
  matches,
  currentUser,
}: {
  users: User[];
  predictions: Prediction[];
  matches: Match[];
  currentUser: User;
}) {
  const ranked = useMemo(() => {
    return users
      .map((u) => {
        const pts = calcUserPoints(u.id, predictions, matches);
        const played = predictions.filter((p) => p.userId === u.id && matches.find((m) => m.id === p.matchId && m.result)).length;
        const exact = predictions.filter((p) => {
          const m = matches.find((mx) => mx.id === p.matchId && mx.result);
          return m ? calcPoints(p, m) === 3 : false;
        }).length;
        return { user: u, pts, played, exact };
      })
      .sort((a, b) => b.pts - a.pts || b.exact - a.exact);
  }, [users, predictions, matches]);

  const medals = ["🥇", "🥈", "🥉"];

  return (
    <div className="space-y-3">
      {ranked.map((entry, i) => {
        const isMe = entry.user.id === currentUser.id;
        return (
          <div
            key={entry.user.id}
            className={`flex items-center gap-4 rounded-2xl px-5 py-4 border transition-all ${
              isMe
                ? "border-primary/40 bg-primary/5"
                : "border-border bg-card hover:border-border/60"
            }`}
          >
            {/* Rank */}
            <div className="w-8 text-center">
              {i < 3 ? (
                <span className="text-xl">{medals[i]}</span>
              ) : (
                <span className="text-sm font-mono font-bold text-muted-foreground">#{i + 1}</span>
              )}
            </div>

            <Avatar user={entry.user} size="md" />

            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-sm truncate">{entry.user.name}</span>
                {isMe && (
                  <span className="text-xs bg-primary/15 text-primary px-1.5 py-0.5 rounded-full border border-primary/25">
                    tú
                  </span>
                )}
              </div>
              <div className="flex items-center gap-3 mt-0.5">
                <span className="text-xs text-muted-foreground">{entry.played} jugados</span>
                <span className="text-xs text-muted-foreground">·</span>
                <span className="text-xs text-primary">{entry.exact} exactos</span>
              </div>
            </div>

            {/* Points */}
            <div className="text-right">
              <span
                className="text-3xl font-black leading-none"
                style={{ fontFamily: "'Barlow Condensed', sans-serif", color: isMe ? "var(--primary)" : "var(--foreground)" }}
              >
                {entry.pts}
              </span>
              <p className="text-xs text-muted-foreground mt-0.5">pts</p>
            </div>
          </div>
        );
      })}

      {/* Legend */}
      <div className="mt-6 rounded-xl border border-border p-4 bg-muted/20">
        <p className="text-xs font-semibold text-muted-foreground mb-3 uppercase tracking-widest">Sistema de puntos</p>
        <div className="grid grid-cols-3 gap-3 text-center">
          {[
            { label: "Resultado exacto", pts: "3", color: "text-primary" },
            { label: "Resultado correcto", pts: "1", color: "text-accent" },
            { label: "Fallo", pts: "0", color: "text-muted-foreground" },
          ].map((r) => (
            <div key={r.label} className="bg-secondary rounded-xl p-3">
              <span className={`text-2xl font-black block ${r.color}`} style={{ fontFamily: "'Barlow Condensed', sans-serif" }}>
                {r.pts}
              </span>
              <span className="text-xs text-muted-foreground leading-tight block mt-1">{r.label}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ─── Main App ─────────────────────────────────────────────────────────────────

type Tab = "partidos" | "clasificacion" | "misporras";
type RoundFilter = "all" | string;

export default function App() {
  const [tab, setTab] = useState<Tab>("partidos");
  const [currentUserId, setCurrentUserId] = useState("u1");
  const [predictions, setPredictions] = useState<Prediction[]>(INITIAL_PREDICTIONS);
  const [roundFilter, setRoundFilter] = useState<RoundFilter>("Jornada 2");
  const [userMenuOpen, setUserMenuOpen] = useState(false);

  const currentUser = USERS.find((u) => u.id === currentUserId)!;

  const rounds = useMemo(() => Array.from(new Set(MATCHES.map((m) => m.round))), []);

  const filteredMatches = useMemo(
    () => (roundFilter === "all" ? MATCHES : MATCHES.filter((m) => m.round === roundFilter)),
    [roundFilter]
  );

  const myPredictions = useMemo(
    () => predictions.filter((p) => p.userId === currentUserId),
    [predictions, currentUserId]
  );

  const myPoints = calcUserPoints(currentUserId, predictions, MATCHES);
  const allUsers = USERS;

  const handlePredict = (matchId: string, a: number, b: number) => {
    setPredictions((prev) => {
      const without = prev.filter((p) => !(p.matchId === matchId && p.userId === currentUserId));
      return [...without, { matchId, userId: currentUserId, scoreA: a, scoreB: b }];
    });
  };

  const upcomingCount = MATCHES.filter((m) => !m.result).length;
  const myPendingCount = MATCHES.filter(
    (m) => !m.result && !predictions.find((p) => p.matchId === m.id && p.userId === currentUserId)
  ).length;

  return (
    <div className="min-h-screen bg-background font-[Outfit]">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-border backdrop-blur-md" style={{ background: "rgba(255, 255, 255, 0.92)" }}>
        <div className="max-w-2xl mx-auto px-4 h-14 flex items-center justify-between gap-4">
          <div className="flex items-center gap-2.5">
            <ImageWithFallback src={logoImg} alt="FIFA World Cup 2026 Logo" className="h-8 w-auto object-contain" />
            <div>
              <h1
                className="text-lg font-black leading-none text-foreground"
                style={{ fontFamily: "'Barlow Condensed', sans-serif", letterSpacing: "0.03em" }}
              >
                MUNDIAL 2026
              </h1>
              <p className="text-xs text-muted-foreground leading-none mt-0.5">Clasificación</p>
            </div>
          </div>

          {/* User switcher */}
          <div className="relative">
            <button
              onClick={() => setUserMenuOpen((v) => !v)}
              className="flex items-center gap-2 rounded-xl bg-secondary border border-border px-3 py-1.5 hover:border-primary/30 transition-all"
            >
              <Avatar user={currentUser} size="sm" />
              <span className="text-sm font-medium hidden sm:block">{currentUser.name}</span>
              <span className="text-xs font-mono font-bold text-primary">{myPoints}pts</span>
              <ChevronDown size={13} className="text-muted-foreground" />
            </button>

            {userMenuOpen && (
              <div className="absolute right-0 top-full mt-2 w-52 rounded-2xl border border-border shadow-2xl z-50 overflow-hidden" style={{ background: "var(--card)" }}>
                <div className="px-3 py-2 border-b border-border">
                  <p className="text-xs text-muted-foreground uppercase tracking-widest font-medium">Cambiar jugador</p>
                </div>
                {USERS.map((u) => {
                  const pts = calcUserPoints(u.id, predictions, MATCHES);
                  return (
                    <button
                      key={u.id}
                      onClick={() => { setCurrentUserId(u.id); setUserMenuOpen(false); }}
                      className={`w-full flex items-center gap-3 px-3 py-2.5 hover:bg-secondary transition-colors ${u.id === currentUserId ? "bg-secondary" : ""}`}
                    >
                      <Avatar user={u} size="sm" />
                      <span className="text-sm flex-1 text-left">{u.name}</span>
                      <span className="text-xs font-mono text-primary font-bold">{pts}pts</span>
                      {u.id === currentUserId && <Check size={13} className="text-primary" />}
                    </button>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Stats bar */}
      <div className="border-b border-border bg-muted/20">
        <div className="max-w-2xl mx-auto px-4 py-3 flex items-center gap-6 overflow-x-auto">
          {[
            { icon: <Trophy size={13} />, label: "Tus puntos", value: `${myPoints} pts`, color: "text-primary" },
            { icon: <Target size={13} />, label: "Pendientes", value: `${myPendingCount} partidos`, color: myPendingCount > 0 ? "text-accent" : "text-muted-foreground" },
            { icon: <Globe size={13} />, label: "Total partidos", value: `${upcomingCount} próximos`, color: "text-muted-foreground" },
          ].map((stat) => (
            <div key={stat.label} className="flex items-center gap-2 shrink-0">
              <span className="text-muted-foreground">{stat.icon}</span>
              <span className="text-xs text-muted-foreground">{stat.label}:</span>
              <span className={`text-xs font-semibold font-mono ${stat.color}`}>{stat.value}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-border sticky top-14 z-40" style={{ background: "rgba(255, 255, 255, 0.95)", backdropFilter: "blur(12px)" }}>
        <div className="max-w-2xl mx-auto px-4 flex gap-0">
          {(
            [
              { id: "partidos", label: "Partidos" },
              { id: "clasificacion", label: "Clasificación" },
              { id: "misporras", label: "Mis porras" },
            ] as const
          ).map((t) => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={`px-4 py-3 text-sm font-semibold border-b-2 transition-all ${
                tab === t.id
                  ? "border-primary text-primary"
                  : "border-transparent text-muted-foreground hover:text-foreground"
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <main className="max-w-2xl mx-auto px-4 py-6">
        {/* ── PARTIDOS ── */}
        {tab === "partidos" && (
          <div className="space-y-5">
            {/* Round filter */}
            <div className="flex gap-2 overflow-x-auto pb-1">
              {rounds.map((r) => (
                <button
                  key={r}
                  onClick={() => setRoundFilter(r)}
                  className={`shrink-0 px-4 py-2 rounded-full text-sm font-medium border transition-all ${
                    roundFilter === r
                      ? "bg-primary text-primary-foreground border-primary"
                      : "border-border text-muted-foreground hover:text-foreground hover:border-foreground/20"
                  }`}
                >
                  {r}
                </button>
              ))}
              <button
                onClick={() => setRoundFilter("all")}
                className={`shrink-0 px-4 py-2 rounded-full text-sm font-medium border transition-all ${
                  roundFilter === "all"
                    ? "bg-primary text-primary-foreground border-primary"
                    : "border-border text-muted-foreground hover:text-foreground"
                }`}
              >
                Todos
              </button>
            </div>

            {filteredMatches.map((match) => (
              <div key={match.id} className="space-y-0">
                <MatchCard
                  match={match}
                  currentUser={currentUser}
                  predictions={predictions}
                  onPredict={handlePredict}
                />
                <AllPredictionsPanel
                  match={match}
                  users={allUsers}
                  predictions={predictions}
                />
              </div>
            ))}
          </div>
        )}

        {/* ── CLASIFICACIÓN ── */}
        {tab === "clasificacion" && (
          <Leaderboard
            users={USERS}
            predictions={predictions}
            matches={MATCHES}
            currentUser={currentUser}
          />
        )}

        {/* ── MIS PORRAS ── */}
        {tab === "misporras" && (
          <div className="space-y-4">
            <div className="flex items-center justify-between mb-2">
              <h2
                className="text-2xl font-black"
                style={{ fontFamily: "'Barlow Condensed', sans-serif" }}
              >
                Mis porras
              </h2>
              <span className="text-xs text-muted-foreground font-mono">{myPredictions.length} registradas</span>
            </div>

            {myPredictions.length === 0 ? (
              <div className="rounded-2xl border border-border bg-card p-12 text-center">
                <Target size={32} className="text-muted-foreground mx-auto mb-3" />
                <p className="text-muted-foreground">Todavía no tienes porras guardadas.</p>
                <button
                  onClick={() => setTab("partidos")}
                  className="mt-4 text-sm text-primary hover:underline"
                >
                  Ir a partidos →
                </button>
              </div>
            ) : (
              <div className="space-y-3">
                {MATCHES.filter((m) => myPredictions.find((p) => p.matchId === m.id)).map((match) => {
                  const pred = myPredictions.find((p) => p.matchId === match.id)!;
                  const pts = match.result ? calcPoints(pred, match) : null;
                  return (
                    <div
                      key={match.id}
                      className="rounded-2xl border border-border bg-card px-5 py-4 flex items-center gap-4"
                    >
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="text-lg">{match.teamA.flag}</span>
                          <span
                            className="text-sm font-bold truncate"
                            style={{ fontFamily: "'Barlow Condensed', sans-serif" }}
                          >
                            {match.teamA.name}
                          </span>
                          <span className="text-muted-foreground">vs</span>
                          <span
                            className="text-sm font-bold truncate"
                            style={{ fontFamily: "'Barlow Condensed', sans-serif" }}
                          >
                            {match.teamB.name}
                          </span>
                          <span className="text-lg">{match.teamB.flag}</span>
                        </div>
                        <p className="text-xs text-muted-foreground mt-0.5">{match.group ?? match.confederation} · {match.date}</p>
                      </div>

                      <div className="flex items-center gap-3 shrink-0">
                        <div className="text-center">
                          <span className="text-xs text-muted-foreground block">Tu porra</span>
                          <span className="text-base font-mono font-bold">
                            {pred.scoreA}–{pred.scoreB}
                          </span>
                        </div>
                        {match.result ? (
                          <div className="text-center">
                            <span className="text-xs text-muted-foreground block">Real</span>
                            <span className="text-base font-mono font-bold text-primary">
                              {match.result.a}–{match.result.b}
                            </span>
                          </div>
                        ) : (
                          <div className="flex items-center gap-1 text-xs text-muted-foreground">
                            <Star size={11} />
                            <span>Pendiente</span>
                          </div>
                        )}
                        {pts !== null && <PointBadge points={pts} />}
                      </div>
                    </div>
                  );
                })}

                {/* Summary */}
                <div className="rounded-2xl border border-primary/30 bg-primary/5 px-5 py-4 flex items-center justify-between mt-2">
                  <span className="text-sm font-semibold">Total de puntos</span>
                  <span
                    className="text-3xl font-black text-primary"
                    style={{ fontFamily: "'Barlow Condensed', sans-serif" }}
                  >
                    {myPoints} pts
                  </span>
                </div>
              </div>
            )}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-border mt-8 py-6 text-center text-xs text-muted-foreground">
        <span>⚽ Porra Mundial 2026 · Clasificatorias</span>
      </footer>
    </div>
  );
}
