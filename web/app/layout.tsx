import type { Metadata } from "next";
import { Space_Grotesk, JetBrains_Mono } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const display = Space_Grotesk({
  variable: "--font-display",
  subsets: ["latin"],
  weight: ["500", "700"],
});
const sans = Space_Grotesk({ variable: "--font-sans", subsets: ["latin"] });
const mono = JetBrains_Mono({ variable: "--font-mono", subsets: ["latin"] });

export const metadata: Metadata = {
  title: "COLLIDER",
  description:
    "Explore real ATLAS Open Data collision events and run a trained classifier " +
    "over their physics features.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className={`${display.variable} ${sans.variable} ${mono.variable}`}>
        <header className="border-b border-edge/60">
          <nav className="mx-auto flex max-w-6xl items-center gap-6 px-6 py-4">
            <Link
              href="/"
              className="font-display text-lg font-bold tracking-[0.2em] text-paper"
            >
              C<span className="text-mint">O</span>LLIDER
            </Link>
            <Link href="/explore" className="text-sm text-muted hover:text-paper">
              Explore
            </Link>
            <Link href="/physics" className="text-sm text-muted hover:text-paper">
              The spectrum
            </Link>
            <Link href="/about" className="text-sm text-muted hover:text-paper">
              How it works
            </Link>
          </nav>
        </header>
        {children}
        <footer className="mt-20 border-t border-edge/60">
          <div className="mx-auto max-w-6xl px-6 py-6 text-xs text-dim">
            Built on{" "}
            <a
              href="https://opendata.cern.ch/record/93910"
              className="text-muted underline decoration-dotted hover:text-paper"
            >
              ATLAS Open Data
            </a>{" "}
            (CC0). Simulated events are labelled as such. Model output is a
            discriminant score, not a probability, and no result here is an
            ATLAS measurement.
          </div>
        </footer>
      </body>
    </html>
  );
}
