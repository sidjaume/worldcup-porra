"use client";

import Link from "next/link";
import { useActionState, useId } from "react";
import { Plus } from "lucide-react";
import { createPoolAction } from "@/app/actions";
import { InviteCodeCopyPanel } from "@/components/pools/InviteCodeForm";
import { Button } from "@/components/ui/Button";
import {
  Field,
  FormMessage,
  FormSuccess,
  SelectInput,
  TextInput,
} from "@/components/ui/Field";
import type { Tournament } from "@/types/api";

export function CreatePoolForm({ tournaments }: { tournaments: Tournament[] }) {
  const [state, action, pending] = useActionState(createPoolAction, {});
  const feedbackId = useId();
  const describedBy = state.error || state.ok ? feedbackId : undefined;

  return (
    <form
      action={action}
      aria-describedby={describedBy}
      className="grid gap-4"
    >
      <Field label="Pool name">
        <TextInput
          aria-describedby={describedBy}
          aria-invalid={state.error ? true : undefined}
          name="name"
          placeholder="Friends and family"
          required
        />
      </Field>
      <Field label="Tournament">
        <SelectInput
          aria-describedby={describedBy}
          aria-invalid={state.error ? true : undefined}
          name="tournament_id"
          required
        >
          <option value="">Select tournament</option>
          {tournaments.map((tournament) => (
            <option key={tournament.id} value={tournament.id}>
              {tournament.name}
            </option>
          ))}
        </SelectInput>
      </Field>
      <FormMessage id={state.error ? feedbackId : undefined} message={state.error} />
      <FormSuccess
        id={state.ok ? feedbackId : undefined}
        message={state.ok ? "Pool created." : undefined}
      />
      {state.inviteCode ? (
        <InviteCodeCopyPanel code={state.inviteCode} title="Initial invite code" />
      ) : null}
      {state.poolId ? (
        <Link
          className="inline-flex min-h-10 items-center justify-center rounded-md border border-line bg-white px-4 py-2 text-sm font-semibold text-ink transition hover:bg-mint focus-visible:outline focus-visible:outline-[3px] focus-visible:outline-offset-2 focus-visible:outline-focus"
          href={`/pools/${state.poolId}`}
        >
          Open pool
        </Link>
      ) : null}
      <Button disabled={pending} type="submit">
        <Plus aria-hidden="true" size={16} />
        {pending ? "Creating" : "Create pool"}
      </Button>
    </form>
  );
}
