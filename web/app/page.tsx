import Link from "next/link";
import { BeamPipeHero } from "@/components/BeamPipeHero";
import { Narrator } from "@/components/Narrator";

/**
 * Landing page.
 *
 * Opens on the detector seen down the beam pipe — the most characteristic
 * thing in this subject's world, built from a real event's measured angles.
 * No event data is fetched and no 3D bundle is loaded (SPEC 6.1, 21.2).
 */
export default function Home() {
  return (
    <main className="grid-bg">
      <section className="mx-auto grid max-w-6xl items-center gap-10 px-6 py-16 lg:grid-cols-[1.1fr_1fr] lg:py-24">
        <div>
          <p className="scrawl text-lg text-hazard">
            Same universe. Smaller things.
          </p>

          <h1 className="mt-3 font-display text-7xl leading-[0.9] tracking-wide text-paper sm:text-8xl">
            C<span className="text-portal">O</span>LLIDER
          </h1>

          <p className="mt-5 max-w-md text-lg leading-relaxed text-muted">
            Real particle collisions from CERN. A classifier that is honest about
            what it knows. And a detector you can spin around.
          </p>

          <div className="mt-8 flex flex-wrap gap-3">
            <Link
              href="/explore"
              className="border-2 border-ink bg-portal px-6 py-3 font-medium text-ground shadow-[3px_3px_0_0_var(--color-ink)] transition-transform hover:translate-x-[1px] hover:translate-y-[1px] hover:shadow-[2px_2px_0_0_var(--color-ink)] focus:outline-none focus-visible:ring-2 focus-visible:ring-portal"
              style={{ borderRadius: "14px 9px 15px 8px" }}
            >
              Open a collision
            </Link>
            <Link
              href="/about"
              className="panel-flat px-6 py-3 font-medium text-paper transition-colors hover:text-portal"
            >
              How it works
            </Link>
          </div>

          <Narrator slot="landing_first_visit" className="mt-10 max-w-md" />
        </div>

        <div className="relative mx-auto w-full max-w-md">
          <div className="panel grain askew-b aspect-square overflow-hidden p-4">
            <BeamPipeHero />
          </div>
          <p className="scrawl mt-3 text-right text-sm leading-tight text-muted">
            looking straight down
            <br />
            the beam pipe ↑
          </p>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-6 pb-20">
        <div className="grid gap-4 sm:grid-cols-3">
          {[
            ["13 TeV", "proton-proton collisions, 2015–2016", "askew-a"],
            ["4", "particles found in the raw data", "askew-b"],
            ["CC0", "open data, every number traceable", "askew-a"],
          ].map(([value, label, tilt]) => (
            <div key={label} className={`panel grain ${tilt} p-5`}>
              <div className="tabular text-2xl text-portal">{value}</div>
              <div className="mt-1 text-xs leading-relaxed text-muted">{label}</div>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
