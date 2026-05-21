import { useEffect, useId, useRef, useState } from "react";

export interface PixelSelectOption {
  value: string;
  label: string;
}

interface Props {
  value: string;
  onChange: (value: string) => void;
  options: PixelSelectOption[];
  placeholder?: string;
  compact?: boolean;
}

export function PixelSelect({
  value,
  onChange,
  options,
  placeholder = "Choose…",
  compact = false,
}: Props) {
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);
  const listId = useId();

  useEffect(() => {
    if (!open) return;
    const onPointerDown = (e: MouseEvent) => {
      if (rootRef.current && !rootRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    document.addEventListener("mousedown", onPointerDown);
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("mousedown", onPointerDown);
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [open]);

  const selected = options.find((o) => o.value === value);
  const display = selected?.label ?? placeholder;

  return (
    <div
      ref={rootRef}
      className={`pixel-select ${compact ? "pixel-select--compact" : ""} ${open ? "is-open" : ""}`}
    >
      <button
        type="button"
        className="pixel-select-trigger"
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-controls={listId}
        onClick={() => setOpen((o) => !o)}
      >
        <span className="pixel-select-label">{display}</span>
        <span className="pixel-select-caret" aria-hidden>
          ▾
        </span>
      </button>

      {open && (
        <ul id={listId} className="pixel-select-menu" role="listbox">
          {options.map((opt) => (
            <li key={opt.value || "__empty"} role="none">
              <button
                type="button"
                role="option"
                aria-selected={value === opt.value}
                className={`pixel-select-option ${value === opt.value ? "is-selected" : ""}`}
                onClick={() => {
                  onChange(opt.value);
                  setOpen(false);
                }}
              >
                {value === opt.value && <span className="pixel-select-check">✓</span>}
                {opt.label}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
