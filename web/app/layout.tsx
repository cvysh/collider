import type { Metadata } from "next";
import { Anton, JetBrains_Mono, Permanent_Marker, Work_Sans } from "next/font/google";
import Link from "next/link";
import "./globals.css";

// Anton: condensed and heavy, for the wordmark and page titles. Work Sans for
// prose. JetBrains Mono carries every number — tabular figures are the
// "pristine" half of the theme. Permanent Marker is for annotation only.
const display = Anton({ variable: "--font-display", subsets: ["latin"], weight: "400" });
const sans = Work_Sans({ variable: "--font-sans", subsets: ["latin"] });
const mono = JetBrains_Mono({ variable: "--font-mono", subsets: ["latin"] });
const marker = Permanent_Marker({
  variable: "--font-marker",
  subsets: ["latin"],
  weight: "400",
});

export const metadata: Metadata = {
  title: "COLLIDER",
  description:
    "Explore real ATLAS Open Data collision events and run a trained classifier " +
    "over their physics features.",
};

const NAV = [
  ["/explore", "Explore"],
  ["/physics", "The spectrum"],
  ["/about", "How it works"],
];

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body
        className={`${display.variable} ${sans.variable} ${mono.variable} ${marker.variable}`}
      >
        <header className="border-b-2 border-ink bg-panel">
          <nav className="mx-auto flex max-w-6xl flex-wrap items-center gap-x-6 gap-y-2 px-6 py-3">
            <Link href="/" className="font-display text-2xl tracking-wide text-paper">
              C<span className="text-portal">O</span>LLIDER
            </Link>
            {NAV.map(([href, label]) => (
              <Link
                key={href}
                href={href}
                className="text-sm text-muted transition-colors hover:text-portal"
              >
                {label}
              </Link>
            ))}
          </nav>
        </header>

        {children}

        <footer className="mt-20 border-t-2 border-ink bg-panel">
          <div className="mx-auto max-w-6xl px-6 py-6">
            <p className="max-w-3xl text-xs leading-relaxed text-dim">
              Built on{" "}
              <a
                href="https://opendata.cern.ch/record/93910"
                className="text-muted underline decoration-dotted hover:text-portal"
              >
                ATLAS Open Data
              </a>{" "}
              (CC0). Simulated events are badged as such. Model output is a
              discriminant score, not a probability, and nothing here is an ATLAS
              measurement.
            </p>
          </div>
        </footer>
      </body>
    </html>
  );
}
