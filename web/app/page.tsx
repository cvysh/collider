import Link from "next/link";
import { Narrator } from "@/components/Narrator";

/**
 * Landing page.
 *
 * Deliberately light: no Three.js, no event data, no API call. SPEC section
 * 6.1 and 21.2 -- the 3D bundle must not load on a page that renders no event.
 */
export default function Home() {
  return (
    <main className="grid-bg">
      <section className="mx-auto flex max-w-6xl flex-col items-start px-6 py-24">
        <p className="font-mono text-xs uppercase tracking-[0.3em] text-muted">
          Same universe. Smaller things. Bigger questions.
        </p>

        <h1 className="mt-6 font-display text-6xl font-bold tracking-[0.12em] text-paper sm:text-7xl">
          C<span className="text-mint">O</span>LLIDER
        </h1>

        <p className="mt-4 max-w-xl text-lg text-muted">
          Real particle collisions from CERN. A trained classifier. And an
          honest account of what it does and doesn&apos;t know.
        </p>

        <div className="mt-10 flex flex-wrap gap-3">
          <Link
            href="/explore"
            className="rounded-lg bg-mint px-6 py-3 font-medium text-void transition-opacity hover:opacity-90 focus:outline-none focus-visible:ring-2 focus-visible:ring-mint/60"
          >
            Explore collisions
          </Link>
          <Link
            href="/about"
            className="panel px-6 py-3 font-medium text-paper transition-colors hover:border-mint/40"
          >
            How it works
          </Link>
        </div>

        <Narrator slot="landing_first_visit" className="mt-14 max-w-xl" />

        <dl className="mt-16 grid gap-6 sm:grid-cols-3">
          {[
            ["13 TeV", "proton-proton collisions, 2015-2016"],
            ["Four resonances", "reproduced from the raw data"],
            ["CC0", "open data, fully traceable"],
          ].map(([value, label]) => (
            <div key={label} className="panel p-4">
              <dt className="tabular text-xl text-mint">{value}</dt>
              <dd className="mt-1 text-xs text-dim">{label}</dd>
            </div>
          ))}
        </dl>
      </section>
    </main>
  );
}
