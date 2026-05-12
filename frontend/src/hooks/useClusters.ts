"use client";

import { useEffect, useState } from "react";
import type { FailureCluster } from "@/types";
import { getClusters } from "@/lib/api";

export function useClusters() {
  const [clusters, setClusters] = useState<FailureCluster[]>([]);
  useEffect(() => {
    getClusters().then(setClusters).catch(() => setClusters([]));
  }, []);
  return clusters;
}
