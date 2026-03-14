'use client';

import React, { useState } from 'react';

/**
 * DecisionSlider — A single input slider with label, value display, and tooltip.
 * 
 * Accessible: ARIA labels, keyboard navigable, high-contrast colors.
 * Mobile: full-width with touch-friendly hit target.
 */

interface DecisionSliderProps {
  id: string;
  label: string;
  min: number;
  max: number;
  step: number;
  value: number;
  unit?: string;
  tooltip?: string;
  infoTooltip?: React.ReactNode;
  onChange: (value: number) => void;
}

export default function DecisionSlider({
  id,
  label,
  min,
  max,
  step,
  value,
  unit = '',
  tooltip = '',
  infoTooltip,
  onChange,
}: DecisionSliderProps) {
  const percentage = ((value - min) / (max - min)) * 100;

  return (
    <div className="mb-4 w-full" title={tooltip}>
      <div className="flex items-center justify-between mb-1">
        <label
          htmlFor={id}
          className="text-sm font-medium text-gray-300 flex items-center"
        >
          {label}
          {infoTooltip}
        </label>
        <span className="text-sm font-mono font-bold text-cyan-400">
          {value}
          {unit && <span className="text-gray-500 ml-0.5">{unit}</span>}
        </span>
      </div>
      <input
        id={id}
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        className="w-full h-2 rounded-lg appearance-none cursor-pointer
                   bg-gray-700 accent-cyan-500
                   focus:outline-none focus:ring-2 focus:ring-cyan-500/50"
        aria-label={`${label}: ${value}${unit}`}
        aria-valuemin={min}
        aria-valuemax={max}
        aria-valuenow={value}
        style={{
          background: `linear-gradient(to right, #06b6d4 0%, #06b6d4 ${percentage}%, #374151 ${percentage}%, #374151 100%)`,
        }}
      />
      <div className="flex justify-between text-xs text-gray-600 mt-0.5">
        <span>{min}{unit}</span>
        <span>{max}{unit}</span>
      </div>
    </div>
  );
}
