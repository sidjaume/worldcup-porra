"use client";

import { useActionState, useId, useState } from "react";
import { Check, Copy, RefreshCw } from "lucide-react";
import { rotateInviteCodeAction } from "@/app/actions";
import { Button } from "@/components/ui/Button";
import { FormMessage } from "@/components/ui/Field";

export function InviteCodeForm({ poolId }: { poolId: string }) {
  const [state, action, pending] = useActionState(rotateInviteCodeAction, {});
  const [confirmed, setConfirmed] = useState(false);
  const [copyStatus, setCopyStatus] = useState<string>();
  const feedbackId = useId();
  const copyStatusId = useId();

  async function copyInviteCode() {
    if (!state.inviteCode) {
      return;
    }
    try {
      await navigator.clipboard.writeText(state.inviteCode);
      setCopyStatus("Invite code copied.");
    } catch {
      setCopyStatus("Copy failed. Select the code and copy it manually.");
    }
  }

  return (
    <form
      action={action}
      aria-describedby={state.error ? feedbackId : undefined}
      className="grid gap-3"
      onSubmit={(event) => {
        if (!confirmed) {
          event.preventDefault();
          return;
        }
        const ok = window.confirm(
          "Rotate this invite code? The current code will stop working for new participants.",
        );
        if (!ok) {
          event.preventDefault();
        }
      }}
    >
      <input name="pool_id" type="hidden" value={poolId} />
      <label className="flex items-start gap-2 text-sm text-slate-700">
        <input
          checked={confirmed}
          className="mt-1"
          onChange={(event) => setConfirmed(event.target.checked)}
          type="checkbox"
        />
        <span>The old invite code will stop working for new joins.</span>
      </label>
      <Button disabled={pending || !confirmed} type="submit" variant="secondary">
        <RefreshCw aria-hidden="true" size={16} />
        {pending ? "Rotating" : "Rotate invite code"}
      </Button>
      {state.inviteCode ? (
        <div
          className="grid gap-3 rounded-md bg-mint px-3 py-3 text-sm text-grass"
          role="status"
        >
          <p className="font-semibold">New invite code</p>
          <div className="flex flex-wrap items-center gap-2">
            <code className="rounded-md bg-white px-2 py-1 font-mono text-sm text-ink">
              {state.inviteCode}
            </code>
            <Button
              aria-describedby={copyStatus ? copyStatusId : undefined}
              onClick={copyInviteCode}
              type="button"
              variant="ghost"
            >
              {copyStatus === "Invite code copied." ? (
                <Check aria-hidden="true" size={16} />
              ) : (
                <Copy aria-hidden="true" size={16} />
              )}
              Copy
            </Button>
          </div>
        </div>
      ) : null}
      <FormMessage id={feedbackId} message={state.error} />
      {copyStatus ? (
        <p className="text-sm font-medium text-grass" id={copyStatusId} role="status">
          {copyStatus}
        </p>
      ) : null}
    </form>
  );
}
