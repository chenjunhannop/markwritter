"use client";

import { MainLayout } from "@/components/layout";
import { SkillList } from "@/components/skills";

export default function SkillsPage() {
  return (
    <MainLayout title="Skills">
      <SkillList />
    </MainLayout>
  );
}