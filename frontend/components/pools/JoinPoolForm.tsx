"use client";

import { useActionState } from "react";
import { Ticket } from "lucide-react";
import { joinPoolAction } from "@/app/actions";
import { Button } from "@/components/ui/Button";
import { Field, FormMessage, TextInput } from "@/components/ui/Field";

export function JoinPoolForm() {
  const [state, action, pending] = useActionState(joinPoolAction, {});

  return (
    <form action={action} className="grid gap-4">
      <Field label="Invite code">
        <TextInput name="invite_code" placeholder="ABCD-1234" required />
      </Field>
      <FormMessage message={state.error} />
      <Button disabled={pending} type="submit" variant="secondary">
        <Ticket aria-hidden="true" size={16} />
        Join pool
      </Button>
    </form>
  );
}
