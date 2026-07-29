"use client";

import { useEffect, useMemo, useState } from "react";
import {
  ArrowDownLeft,
  Building2,
  ChevronDown,
  Landmark,
  ReceiptText,
  Search,
  ShoppingBag,
  Smartphone,
} from "lucide-react";
import { CustomerPicker } from "@/components/customer-picker";
import { EmptyState, ErrorState, LoadingState } from "@/components/data-state";
import { SecurePage } from "@/components/secure-page";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  createBankingTransaction,
  Customer,
  listCustomers,
  listTransactions,
  Transaction,
} from "@/services/platform";
import { isCredit, money, transactionDirection, transactionLabel } from "@/utils/finance";

const actions = [
  { label: "Salary Received", type: "salary", category: "income", merchant: "Employer" },
  { label: "Cash Deposit", type: "deposit", category: "income", merchant: "Bank deposit" },
  { label: "Cash Withdrawal", type: "withdrawal", category: "cash", merchant: "ATM" },
  { label: "Transfer", type: "transfer", category: "transfer", merchant: "Transfer recipient" },
  { label: "Merchant Payment", type: "merchant_payment", category: "shopping", merchant: "Merchant" },
  { label: "UPI Payment", type: "upi_payment", category: "payments", merchant: "UPI merchant" },
  { label: "Utility Bill", type: "bill", category: "utilities", merchant: "Electricity" },
  { label: "Subscription", type: "subscription", category: "subscriptions", merchant: "Netflix" },
];

const filters = ["All", "Credits", "Debits", "Merchant", "Bills", "Transfers", "Salary", "UPI"] as const;
type Filter = (typeof filters)[number];

const icon = (type: string) =>
  type === "salary" || type === "deposit" ? <ArrowDownLeft className="text-emerald-600" /> :
  type === "transfer" ? <Landmark /> :
  type === "bill" ? <ReceiptText /> :
  ["upi", "upi_payment"].includes(type) ? <Smartphone /> :
  type === "withdrawal" ? <Building2 /> :
  <ShoppingBag />;

const matchesFilter = (item: Transaction, filter: Filter) => {
  const type = item.transaction_type.toLowerCase();
  if (filter === "Credits") return isCredit(type);
  if (filter === "Debits") return !isCredit(type);
  if (filter === "Merchant") return ["merchant", "merchant_payment"].includes(type);
  if (filter === "Bills") return type === "bill";
  if (filter === "Transfers") return type === "transfer";
  if (filter === "Salary") return type === "salary";
  if (filter === "UPI") return ["upi", "upi_payment"].includes(type);
  return true;
};

export default function TransactionsPage() {
  const [customers, setCustomers] = useState<Customer[] | null>(null);
  const [customerId, setCustomerId] = useState("");
  const [items, setItems] = useState<Transaction[] | null>(null);
  const [amount, setAmount] = useState("");
  const [actionIndex, setActionIndex] = useState(0);
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<Filter>("All");
  const [expanded, setExpanded] = useState<string | null>(null);
  const [error, setError] = useState("");

  const loadHistory = (id: string) =>
    listTransactions({ customer_id: id, page_size: 100 })
      .then((result) => setItems(result.items))
      .catch(() => setError("Unable to load account activity."));

  const loadAccounts = async (preferredId?: string) => {
    try {
      const result = await listCustomers();
      setCustomers(result.items);
      const nextId = preferredId || customerId || result.items[0]?.customer_id || "";
      setCustomerId(nextId);
      if (nextId) await loadHistory(nextId);
    } catch {
      setError("Unable to load your accounts.");
    }
  };

  useEffect(() => {
    void loadAccounts();
    // Initial account selection is intentionally resolved by the loader.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const visible = useMemo(
    () => (items ?? []).filter((item) => {
      const text = `${item.merchant ?? ""} ${item.category} ${transactionLabel(item.transaction_type, item.category)}`.toLowerCase();
      return text.includes(query.toLowerCase()) && matchesFilter(item, filter);
    }),
    [filter, items, query],
  );
  const selected = customers?.find((customer) => customer.customer_id === customerId);

  async function submit() {
    const choice = actions[actionIndex];
    if (!customerId || !Number(amount)) return;
    try {
      setError("");
      await createBankingTransaction(customerId, Number(amount), {
        transaction_type: choice.type,
        category: choice.category,
        merchant: choice.merchant,
      });
      setAmount("");
      await loadAccounts(customerId);
    } catch {
      setError("We could not record this banking operation.");
    }
  }

  return (
    <SecurePage title="Money" description="Protected account activity with live fraud intelligence.">
      <div className="space-y-6">
        {error ? <ErrorState message={error} onRetry={() => void loadAccounts(customerId)} /> :
          customers === null ? <LoadingState label="Loading accounts…" /> :
          !customers.length ? <EmptyState title="No connected accounts" description="Connect an account to record banking activity." /> :
          <>
            <CustomerPicker customers={customers} value={customerId} onChange={(id) => {
              setCustomerId(id);
              setItems(null);
              void loadHistory(id);
            }} />
            <Card>
              <CardHeader>
                <CardDescription>Available balance</CardDescription>
                <CardTitle className="text-4xl">{money(selected?.account_balance)}</CardTitle>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Make a banking movement</CardTitle>
                <CardDescription>Each operation updates your balance and real-time intelligence.</CardDescription>
              </CardHeader>
              <CardContent className="grid gap-3 md:grid-cols-[1fr_160px_auto]">
                <select aria-label="Banking operation" className="h-11 rounded-xl border border-border bg-background px-3 text-sm" value={actionIndex} onChange={(event) => setActionIndex(Number(event.target.value))}>
                  {actions.map((item, index) => <option key={item.type} value={index}>{item.label}</option>)}
                </select>
                <Input aria-label="Amount" type="number" min="0.01" value={amount} onChange={(event) => setAmount(event.target.value)} placeholder="Amount in ₹" />
                <Button onClick={submit}>Confirm</Button>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Transaction history</CardTitle>
                <CardDescription>Every movement is checked by the Fraud Center.</CardDescription>
                <div className="grid gap-2 pt-3 sm:grid-cols-[1fr_180px]">
                  <div className="relative">
                    <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Input className="pl-9" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search merchant or category" />
                  </div>
                  <select aria-label="Transaction filter" className="h-11 rounded-xl border border-border bg-background px-3 text-sm" value={filter} onChange={(event) => setFilter(event.target.value as Filter)}>
                    {filters.map((value) => <option key={value}>{value}</option>)}
                  </select>
                </div>
              </CardHeader>
              <CardContent>
                {items === null ? <LoadingState /> :
                  !visible.length ? <EmptyState title="No matching transactions" description="Try a different search or filter, or record a new operation." /> :
                  <div className="divide-y divide-border">
                    {visible.map((item) => {
                      const direction = transactionDirection(item.transaction_type);
                      return <div key={item.transaction_id}>
                        <button aria-expanded={expanded === item.transaction_id} onClick={() => setExpanded(expanded === item.transaction_id ? null : item.transaction_id)} className="grid w-full gap-3 py-4 text-left sm:grid-cols-[auto_1.2fr_1fr_auto_auto] sm:items-center">
                          <span className="w-fit rounded-xl bg-muted p-2">{icon(item.transaction_type)}</span>
                          <span>
                            <span className="block font-medium">{transactionLabel(item.transaction_type, item.category)}</span>
                            <span className="block text-sm text-muted-foreground">Merchant: {item.merchant || "Not provided"}</span>
                          </span>
                          <span className="text-sm text-muted-foreground">
                            <span className="block">Category: {item.category || "Other"}</span>
                            <span className="block">Status: {item.status}</span>
                            <span className="block">Date: {item.transaction_date}</span>
                          </span>
                          <span className={`font-semibold ${direction === "Credit" ? "text-emerald-600" : "text-rose-600"}`}>
                            {direction} {direction === "Credit" ? "+" : "−"}{money(item.transaction_amount)}
                          </span>
                          <ChevronDown className={`h-4 w-4 transition-transform ${expanded === item.transaction_id ? "rotate-180" : ""}`} />
                        </button>
                        {expanded === item.transaction_id && <div className="mb-4 grid gap-2 rounded-xl bg-muted/50 p-4 text-sm sm:grid-cols-2">
                          <span>Operation Type: {transactionLabel(item.transaction_type, item.category)}</span>
                          <span>Direction: {direction}</span>
                          <span>Timestamp: {item.transaction_date} {item.transaction_time}</span>
                          <span>Transaction ID: {item.transaction_id}</span>
                          <span className="sm:col-span-2">Fraud review: available in Fraud Center after runtime assessment.</span>
                        </div>}
                      </div>;
                    })}
                  </div>}
              </CardContent>
            </Card>
          </>}
      </div>
    </SecurePage>
  );
}
