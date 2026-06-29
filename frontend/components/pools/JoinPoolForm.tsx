"use client";

import { useActionState, useId } from "react";
import { Ticket } from "lucide-react";
import { joinPoolAction } from "@/app/actions";
import { Button } from "@/components/ui/Button";
import { Field, FormMessage, TextInput } from "@/components/ui/Field";

export function JoinPoolForm() {
  const [state, action, pending] = useActionState(joinPoolAction, {});
  const feedbackId = useId();

  return (
    <form
      action={action}
      aria-describedby={state.error ? feedbackId : undefined}
      className="grid gap-4"
    >
      <Field label="Invite code">
        <TextInput
          aria-describedby={state.error ? feedbackId : undefined}
          aria-invalid={state.error ? true : undefined}
          name="invite_code"
          placeholder="ABCD-1234"
          required
        />
      </Field>
      <FormMessage id={feedbackId} message={state.error} />
      <Button disabled={pending} type="submit" variant="secondary">
        <Ticket aria-hidden="true" size={16} />
        {pending ? "Joining" : "Join pool"}
      </Button>
    </form>
  );
}
