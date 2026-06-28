import { AppShell } from "@/components/layout/AppShell";
import { CreatePoolForm } from "@/components/pools/CreatePoolForm";
import { JoinPoolForm } from "@/components/pools/JoinPoolForm";
import { PoolSelector } from "@/components/pools/PoolSelector";
import { Card } from "@/components/ui/Card";
import { listPools } from "@/lib/api/pools";
import { listTournaments } from "@/lib/api/tournaments";
import { requireSession } from "@/lib/auth/require-session";

export default async function PoolsPage() {
  const session = await requireSession();
  const [pools, tournaments] = await Promise.all([
    listPools(session.accessToken),
    listTournaments(session.accessToken),
  ]);

  return (
    <AppShell user={session.user}>
      <div className="grid gap-6">
        <header>
          <h1 className="text-3xl font-bold">Pools</h1>
          <p className="mt-2 text-slate-600">
            Create a private pool or join one with an invite code.
          </p>
        </header>
        <PoolSelector pools={pools} />
        <div className="grid gap-4 lg:grid-cols-2">
          <Card>
            <h2 className="mb-4 text-lg font-semibold">Create pool</h2>
            <CreatePoolForm tournaments={tournaments} />
          </Card>
          <Card>
            <h2 className="mb-4 text-lg font-semibold">Join pool</h2>
            <JoinPoolForm />
          </Card>
        </div>
      </div>
    </AppShell>
  );
}
