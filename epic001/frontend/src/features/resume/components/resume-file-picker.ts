import {
  type ChangeEvent,
  createElement,
  Fragment,
  type FormEvent,
} from "react";

const FILE_INPUT_ID = "resume-file-input";

type FileInputEventHandler = (
  event: ChangeEvent<HTMLInputElement> | FormEvent<HTMLInputElement>,
) => void;

export function fileInputEventProps(handler: FileInputEventHandler) {
  return {
    onChange: handler,
    onInput: handler,
  };
}

export function selectedFileFromInput(
  input: Pick<HTMLInputElement, "files"> | null,
): File | null {
  return input?.files?.[0] ?? null;
}

export function ResumeFilePicker({
  buttonLabel,
  disabled,
  onChange,
  onAnalyze,
  analyzeLabel = "Analyze Resume",
}: {
  buttonLabel: string;
  disabled: boolean;
  onChange: FileInputEventHandler;
  onAnalyze: (file: File | null) => void;
  analyzeLabel?: string;
}) {
  return createElement(
    Fragment,
    null,
    createElement(
      "label",
      {
        htmlFor: FILE_INPUT_ID,
        className: disabled ? "drop-zone is-disabled" : "drop-zone",
      },
      createElement(
        "span",
        { className: "document-icon", "aria-hidden": true },
        "📄",
      ),
      createElement("strong", null, "Drag & Drop Resume Here"),
      createElement("span", null, "or"),
      createElement("span", null, "Click to Upload"),
    ),
    createElement(
      "div",
      { className: "native-file-control" },
      createElement("span", { className: "native-file-label" }, buttonLabel),
      createElement("input", {
        id: FILE_INPUT_ID,
        type: "file",
        accept: ".pdf,.doc,.docx",
        className: "native-file-input",
        "aria-label": buttonLabel,
        disabled,
        ...fileInputEventProps(onChange),
      }),
    ),
    createElement(
      "button",
      {
        type: "button",
        className: "primary-button",
        disabled,
        onClick: () => {
          const input = document.getElementById(FILE_INPUT_ID);
          onAnalyze(
            input instanceof HTMLInputElement
              ? selectedFileFromInput(input)
              : null,
          );
        },
      },
      analyzeLabel,
    ),
  );
}
