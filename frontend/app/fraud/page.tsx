import { CustomerIntelligencePage } from "@/components/customer-intelligence-page";
export default function FraudPage() { return <CustomerIntelligencePage title="Fraud Center" description="Fraud score, risk level, explanations, history, and analytics." endpoint="/fraud/risk-summary/:customerId" emptyTitle="No fraud intelligence data"/>; }
