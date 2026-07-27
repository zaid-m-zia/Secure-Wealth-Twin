import { CustomerIntelligencePage } from "@/components/customer-intelligence-page";
export default function WealthPage() { return <CustomerIntelligencePage title="Digital Wealth Twin" description="Financial DNA, lifestyle, health, spending capacity, and investment readiness." endpoint="/wealth/:customerId" emptyTitle="No wealth twin data"/>; }
