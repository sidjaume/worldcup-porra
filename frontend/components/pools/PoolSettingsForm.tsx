"use client";

import { useActionState } from "react";
import { Save } from "lucide-react";
import { updatePoolAction } from "@/app/actions";
import { Button } from "@/components/ui/Button";
import { Field, FormMessage, TextInput } from "@/components/ui/Field";
import type { PoolDetail } from "@/types/api";

export function PoolSettingsForm({ pool }: { pool: PoolDetail }) {
  const [state, action, pending] = useActionState(updatePoolAction, {});

  return (
    <form action={action} className="grid gap-4">
      <input name="pool_id" type="hidden" value={pool.id} />
      <Field label="Pool name">
        <TextInput defaultValue={pool.name} name="name" required />
      </Field>
      <label className="flex items-center gap-2 text-sm font-medium">
        <input defaultChecked={pool.is_active ?? true} name="is_active" type="checkbox" />
        Active
      </label>
      <FormMessage message={state.error} />
      {state.ok ? <p className="text-sm font-medium text-grass">Saved.</p> : null}
      <Button disabled={pending} type="submit">
        <Save aria-hidden="true" size={16} />
        Save pool
      </Button>
    </form>
  );
}
