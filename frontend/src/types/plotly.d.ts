declare module 'plotly.js-dist-min' {
  export function newPlot(
    root: HTMLElement,
    data: any[],
    layout?: any,
    config?: any
  ): Promise<any>;
  export function react(
    root: HTMLElement,
    data: any[],
    layout?: any,
    config?: any
  ): Promise<any>;
  export function purge(root: HTMLElement): void;
  export type Data = any;
  export type Layout = any;
  export type Config = any;
}
