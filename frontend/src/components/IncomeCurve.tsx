'use client';

import React, { useEffect, useRef } from 'react';

/**
 * IncomeCurve — Plotly chart showing income trajectory with:
 * - Median line + percentile bands (5th-95th, 25th-75th)
 * - Optional Scenario B overlay in purple
 * - Currency-aware formatting (USD / INR)
 */

interface PercentileData {
  percentiles: Record<number, number[]>;
  sample_trajectories: number[][];
}

interface SimulationData {
  years: number[];
  income: PercentileData;
  happiness: PercentileData;
  stress: PercentileData;
}

type Currency = 'USD' | 'INR';

const CURRENCY_CONFIG = {
  USD: { symbol: '$', rate: 1 },
  INR: { symbol: '₹', rate: 83 },
} as const;

interface IncomeCurveProps {
  data: SimulationData | null;
  dataB?: SimulationData | null;
  loading?: boolean;
  currency?: Currency;
}

export default function IncomeCurve({ data, dataB, loading = false, currency = 'USD' }: IncomeCurveProps) {
  const chartRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!data || !chartRef.current) return;

    import('plotly.js-dist-min').then((Plotly) => {
      const { years, income } = data;
      const p = income.percentiles;
      const rate = CURRENCY_CONFIG[currency].rate;
      const sym = CURRENCY_CONFIG[currency].symbol;
      const convert = (arr: number[]) => arr.map(v => v * rate);

      const traces: any[] = [
        // Scenario A: 5th-95th band
        {
          x: [...years, ...years.slice().reverse()],
          y: [...convert(p[95] || []), ...convert(p[5] || []).slice().reverse()],
          fill: 'toself', fillcolor: 'rgba(6, 182, 212, 0.08)',
          line: { color: 'transparent' }, name: 'A: 5th–95th', showlegend: true,
          hoverinfo: 'skip', type: 'scatter',
        },
        // Scenario A: 25th-75th band
        {
          x: [...years, ...years.slice().reverse()],
          y: [...convert(p[75] || []), ...convert(p[25] || []).slice().reverse()],
          fill: 'toself', fillcolor: 'rgba(6, 182, 212, 0.18)',
          line: { color: 'transparent' }, name: 'A: 25th–75th', showlegend: true,
          hoverinfo: 'skip', type: 'scatter',
        },
        // Scenario A: Median line
        {
          x: years, y: convert(p[50] || []),
          mode: 'lines', line: { color: '#06b6d4', width: 3 },
          name: dataB ? 'Scenario A (median)' : 'Median',
          hovertemplate: `Year %{x}<br>${sym}%{y:,.0f}<extra></extra>`,
          type: 'scatter',
        },
      ];

      // Scenario A sample paths
      (income.sample_trajectories || []).slice(0, 2).forEach((traj, i) => {
        traces.push({
          x: years, y: convert(traj),
          mode: 'lines', line: { color: '#06b6d4', width: 1, dash: 'dot' },
          opacity: 0.3, name: i === 0 ? 'A: samples' : '', showlegend: i === 0,
          hoverinfo: 'skip', type: 'scatter',
        });
      });

      // Scenario B overlay
      if (dataB) {
        const pb = dataB.income.percentiles;
        const yearsB = dataB.years;
        // B: 25th-75th band
        traces.push({
          x: [...yearsB, ...yearsB.slice().reverse()],
          y: [...convert(pb[75] || []), ...convert(pb[25] || []).slice().reverse()],
          fill: 'toself', fillcolor: 'rgba(168, 85, 247, 0.12)',
          line: { color: 'transparent' }, name: 'B: 25th–75th',
          hoverinfo: 'skip', type: 'scatter',
        });
        // B: Median line
        traces.push({
          x: yearsB, y: convert(pb[50] || []),
          mode: 'lines', line: { color: '#a855f7', width: 3, dash: 'dash' },
          name: 'Scenario B (median)',
          hovertemplate: `Year %{x}<br>${sym}%{y:,.0f}<extra></extra>`,
          type: 'scatter',
        });
      }

      const layout: any = {
        title: {
          text: dataB
            ? `Income Trajectory — Scenario Comparison (${currency})`
            : `Income Trajectory (${currency})`,
          font: { color: '#e2e8f0', size: 16 },
        },
        paper_bgcolor: 'transparent', plot_bgcolor: 'transparent',
        font: { color: '#94a3b8' },
        xaxis: { title: 'Years from now', gridcolor: '#1e293b', zerolinecolor: '#334155' },
        yaxis: {
          title: `Annual Income (${currency})`,
          gridcolor: '#1e293b', zerolinecolor: '#334155',
          tickformat: currency === 'USD' ? '$,.0f' : ',.0f',
          tickprefix: currency === 'INR' ? '₹' : '',
        },
        legend: { x: 0, y: 1.15, orientation: 'h', font: { size: 10 } },
        margin: { l: 90, r: 20, t: 50, b: 50 },
        hovermode: 'x unified',
      };

      Plotly.newPlot(chartRef.current!, traces, layout, { responsive: true, displayModeBar: false });
    });
  }, [data, dataB, currency]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-80 bg-gray-900/50 rounded-xl border border-gray-800">
        <div className="animate-pulse text-cyan-400">
          <svg className="animate-spin h-8 w-8 mr-2 inline" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          Running simulations…
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex items-center justify-center h-80 bg-gray-900/50 rounded-xl border border-gray-800 text-gray-500">
        Adjust your inputs and click &quot;Run Simulation&quot; to see your trajectory
      </div>
    );
  }

  return (
    <div className="bg-gray-900/50 rounded-xl border border-gray-800 p-4">
      <div ref={chartRef} className="w-full h-80" />
      <p className="text-xs text-gray-600 mt-2 text-center">
        {dataB
          ? 'Blue = Scenario A · Purple = Scenario B · Shaded areas show percentile ranges.'
          : 'Shaded bands show 5th–95th and 25th–75th percentile ranges from Monte Carlo simulation.'}
      </p>
    </div>
  );
}
