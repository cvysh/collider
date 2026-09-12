import Link from "next/link";
import { Narrator } from "@/components/Narrator";

export default function NotFound() {
  return (
    <main className="mx-auto max-w-6xl px-6 py-24">
      <h1 className="font-display text-3xl tracking-wide text-paper">Not found</h1>
      <Narrator slot="event_not_found" className="mt-6 max-w-xl" />
      <Link href="/explore" className="mt-6 inline-block text-sm text-portal hover:underline">
        Back to explore
      </Link>
    </main>
  );
}
