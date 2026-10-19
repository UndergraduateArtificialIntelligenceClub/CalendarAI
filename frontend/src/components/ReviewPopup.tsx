import type { Deadline } from "../types";

// Review popup shown on the upload page after parsing: issue #29
// Walks through each parsed deadline with its source_text so the user can edit, delete or confirm it.
type Props = {
  pending: Deadline[];
  onDone: (confirmed: Deadline[]) => void;
};

function ReviewPopup({ pending, onDone }: Props) {
  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black/40">
      <div className="rounded-lg bg-white p-6">
        <p>Review {pending.length} deadlines. Coming soon.</p>
        <button className="mt-4 text-blue-600" onClick={() => onDone(pending)}>
          Confirm all
        </button>
      </div>
    </div>
  );
}

export default ReviewPopup;
