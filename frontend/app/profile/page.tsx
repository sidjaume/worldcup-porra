import { AppShell } from "@/components/layout/AppShell";
import { ProfileForm } from "@/components/profile/ProfileForm";
import { Card } from "@/components/ui/Card";
import { requireSession } from "@/lib/auth/require-session";

export default async function ProfilePage() {
  const session = await requireSession();

  return (
    <AppShell user={session.user}>
      <div className="grid max-w-2xl gap-6">
        <header>
          <h1 className="text-3xl font-bold">Profile</h1>
          <p className="mt-2 text-slate-600">Manage your display name.</p>
        </header>
        <Card>
          <ProfileForm user={session.user} />
        </Card>
      </div>
    </AppShell>
  );
}
