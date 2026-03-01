import { PropsWithChildren } from 'react';

type HoloCardProps = PropsWithChildren<{ title: string }>;

export function HoloCard({ title, children }: HoloCardProps) {
  return (
    <section className="holo-card">
      <header><h2>{title}</h2></header>
      <div>{children}</div>
    </section>
  );
}
