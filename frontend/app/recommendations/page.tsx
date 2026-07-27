import { CustomerIntelligencePage } from "@/components/customer-intelligence-page";
export default function RecommendationsPage() { return <CustomerIntelligencePage title="Financial Decision Intelligence" description="Personalized recommendations, ranking, confidence, and explanations." endpoint="/recommendations/:customerId" emptyTitle="No recommendations"/>; }
