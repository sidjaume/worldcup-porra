"use client";

import { useActionState } from "react";
import { RefreshCw } from "lucide-react";
import { rotateInviteCodeAction } from "@/app/actions";
import { Button } from "@/components/ui/Button";
import { FormMessage } from "@/components/ui/Field";

export function InviteCodeForm({ poolId }: { poolId: string }) {
  const [state, action, pending] = useActionState(rotateInviteCodeAction, {});

  return (
    <form action={action} className="grid gap-3">
      <input name="pool_id" type="hidden" value={poolId} />
      <Button disabled={pending} type="submit" variant="secondary">
        <RefreshCw aria-hidden="true" size={16} />
        Rotate invite code
      </Button>
      {state.inviteCode ? (
        <p className="rounded-md bg-mint px-3 py-2 text-sm font-semibold text-grass">
          New invite code: {state.inviteCode}
        </p>
      ) : null}
      <FormMessage message={state.error} />
    </form>
  );
}
