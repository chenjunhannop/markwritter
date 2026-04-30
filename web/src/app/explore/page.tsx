import { BaseLayout } from "@/components/layouts/base-layout";
import { ExplorePage as ExplorePageContent } from "@/features/explore/explore-page";

export default function ExplorePage() {
  return (
    <BaseLayout>
      <div className="h-[calc(100vh-var(--header-height)-4rem)]">
        <ExplorePageContent />
      </div>
    </BaseLayout>
  );
}
