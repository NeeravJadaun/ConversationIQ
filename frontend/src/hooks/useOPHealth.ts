"use client";

import { useEffect, useState } from "react";
import type { OperatingProcedure } from "@/types";
import { getProcedures } from "@/lib/api";

export function useOPHealth() {
  const [procedures, setProcedures] = useState<OperatingProcedure[]>([]);
  useEffect(() => {
    getProcedures().then(setProcedures).catch(() => setProcedures([]));
  }, []);
  return procedures;
}
