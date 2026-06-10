import * as echarts from "echarts";
import { useEffect, useRef } from "react";

type EChartProps = {
  option: echarts.EChartsOption;
  height?: number;
  ariaLabel: string;
};

export function EChart({ option, height = 320, ariaLabel }: EChartProps) {
  const elementRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!elementRef.current) return undefined;
    const chart = echarts.init(elementRef.current, undefined, { renderer: "canvas" });
    chart.setOption(option, true);

    const resize = () => chart.resize();
    window.addEventListener("resize", resize);
    const observer = new ResizeObserver(resize);
    observer.observe(elementRef.current);

    return () => {
      observer.disconnect();
      window.removeEventListener("resize", resize);
      chart.dispose();
    };
  }, [option]);

  return <div className="echart" role="img" aria-label={ariaLabel} ref={elementRef} style={{ height }} />;
}
