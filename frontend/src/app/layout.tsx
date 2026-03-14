import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'ChronoPath — Explore How Your Decisions Shape Your Future',
  description:
    'ChronoPath is an AI-powered life decision simulator. Predict income, happiness, and stress trajectories using behavioral modeling and Monte Carlo simulation.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
