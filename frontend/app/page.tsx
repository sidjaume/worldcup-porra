import Link from "next/link";
import { ArrowRight, ShieldCheck, Trophy, Users } from "lucide-react";
import { LoginButton } from "@/components/auth/LoginButton";
import { AppShell } from "@/components/layout/AppShell";
import { Card } from "@/components/ui/Card";
import { listPools } from "@/lib/api/pools";
import { listTournaments } from "@/lib/api/tournaments";
import { getSession } from "@/lib/auth/session";
import { requireSession } from "@/lib/auth/require-session";

export default async function HomePage({
  searchParams,
}: {
  searchParams: Promise<{ auth_error?: string }>;
}) {
  const session = await getSession();
  if (!session) {
    const { auth_error: authError } = await searchParams;
    return <LoginScreen authError={authError} />;
  }

  const authed = await requireSession();
  const [pools, tournaments] = await Promise.all([
    listPools(authed.accessToken),
    listTournaments(authed.accessToken),
  ]);

  return (
    <AppShell user={authed.user}>
      <div className="grid gap-6">
        <section className="grid gap-2">
          <p className="text-sm font-semibold uppercase tracking-wide text-grass">
            FIFA World Cup 2026
          </p>
          <h1 className="text-3xl font-bold sm:text-4xl">Your knockout pool</h1>
          <p className="max-w-2xl text-slate-600">
            Manage private pools, submit match predictions, and follow live rankings.
          </p>
        </section>
        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <p className="text-sm text-slate-600">Pools</p>
            <p className="mt-2 text-3xl font-bold">{pools.length}</p>
          </Card>
          <Card>
            <p className="text-sm text-slate-600">Available tournaments</p>
            <p className="mt-2 text-3xl font-bold">{tournaments.length}</p>
          </Card>
          <Card>
            <p className="text-sm text-slate-600">Scoring</p>
            <p className="mt-2 text-lg font-semibold">Up to 4 points per match</p>
          </Card>
        </div>
        <Link
          className="inline-flex w-fit items-center gap-2 rounded-md border border-grass bg-grass px-4 py-2 text-sm font-semibold text-white"
          href="/pools"
        >
          Open pools
          <ArrowRight aria-hidden="true" size={16} />
        </Link>
      </div>
    </AppShell>
  );
}

function LoginScreen({ authError }: { authError?: string }) {
  return (
    <main className="min-h-screen">
      <section className="mx-auto grid min-h-screen max-w-6xl content-center gap-10 px-4 py-10 sm:px-6 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
        <div className="grid gap-6">
          <div className="inline-flex w-fit items-center gap-2 rounded-md bg-mint px-3 py-2 text-sm font-semibold text-grass">
            <Trophy aria-hidden="true" size={16} />
            Knockout predictions
          </div>
          <div className="grid gap-4">
            <h1 className="text-4xl font-bold leading-tight sm:text-5xl">
              World Cup Pool
            </h1>
            <p className="max-w-xl text-lg text-slate-600">
              A private prediction pool for the FIFA World Cup 2026 knockout rounds.
            </p>
          </div>
          {authError ? (
            <p className="rounded-md border border-coral bg-white px-4 py-3 text-sm font-medium text-coral">
              Sign-in could not be completed. Please try again.
            </p>
          ) : null}
          <LoginButton />
        </div>
        <div className="grid gap-4">
          <Card>
            <div className="flex gap-3">
              <ShieldCheck className="mt-1 text-grass" aria-hidden="true" size={22} />
              <div>
                <h2 className="font-semibold">Backend-owned authentication</h2>
                <p className="mt-1 text-sm text-slate-600">
                  Google OAuth is handled by the API. The frontend never receives Google secrets.
                </p>
              </div>
            </div>
          </Card>
          <Card>
            <div className="flex gap-3">
              <Users className="mt-1 text-gold" aria-hidden="true" size={22} />
              <div>
                <h2 className="font-semibold">Private groups</h2>
                <p className="mt-1 text-sm text-slate-600">
                  Join with an invite code, make predictions, and compare rankings.
                </p>
              </div>
            </div>
          </Card>
        </div>
      </section>
    </main>
  );
}
