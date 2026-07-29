import { Transaction } from "@/services/platform";

export const incomeTypes = new Set(["salary", "deposit", "income", "refund"]);
export const isCredit = (type: string) => incomeTypes.has(type.toLowerCase());
export const transactionDirection = (type: string) => isCredit(type) ? "Credit" : "Debit";
export const money = (value: number | null | undefined) => `₹${Number(value ?? 0).toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;
export const pct = (value: number | null | undefined) => `${Math.round(Number(value ?? 0))}%`;
export const transactionLabel = (type: string, category?: string | null) => {
  const labels: Record<string, string> = {
    salary: "Salary Received",
    deposit: "Cash Deposit",
    withdrawal: "Cash Withdrawal",
    transfer: "Transfer",
    merchant: "Merchant Payment",
    merchant_payment: "Merchant Payment",
    upi: "UPI Payment",
    upi_payment: "UPI Payment",
    bill: "Utility Bill",
    subscription: "Subscription",
  };
  const normalizedType = type.toLowerCase();
  if (labels[normalizedType]) return labels[normalizedType];
  const normalizedCategory = (category ?? "").toLowerCase();
  if (normalizedCategory === "salary") return labels.salary;
  if (["bill", "bills", "utilities"].includes(normalizedCategory)) return labels.bill;
  if (["subscription", "subscriptions"].includes(normalizedCategory)) return labels.subscription;
  if (normalizedCategory === "transfer") return labels.transfer;
  if (normalizedCategory === "upi") return labels.upi;
  // Imported legacy expense rows lack operation metadata; classify them consistently
  // with the runtime engine's debit treatment instead of displaying a generic label.
  return labels.merchant;
};
export const categoryBreakdown = (transactions: Transaction[]) => Object.entries(transactions.reduce<Record<string, number>>((totals, transaction) => {
  if (!isCredit(transaction.transaction_type)) totals[transaction.category || "other"] = (totals[transaction.category || "other"] ?? 0) + transaction.transaction_amount;
  return totals;
}, {})).map(([name, value]) => ({ name, value })).sort((left, right) => right.value - left.value);
export const level = (score: number | null | undefined) => {
  const value = Number(score ?? 0);
  if (value >= 75) return "Excellent";
  if (value >= 55) return "Good";
  if (value >= 35) return "Fair";
  return "Needs attention";
};
