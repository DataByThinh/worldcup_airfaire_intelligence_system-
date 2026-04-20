import { useMemo, useState } from "react";
import {
  Plane,
  CalendarDays,
  Clock3,
  BadgeDollarSign,
  Lightbulb,
  RefreshCw,
  Info,
  Ticket,
  Map,
  ShieldCheck,
} from "lucide-react";

export default function WorldCupAirfareRecommendationUI() {
  const routes = [
    {
      route: "BOS-MIA",
      tag: "Wait for sweet spot",
      bestWindow: "30 days",
      bestWindowDays: 30,
      bestPrice: 294,
      d90: 320,
      d30: 294,
      d10: 411,
      d1: 561,
      cheapestAirline: "Frontier Airlines",
      cheapestAirlinePrice: 272,
      airlines: [
        { name: "Frontier Airlines", price: 272, note: "Cheapest" },
        { name: "JetBlue Airways", price: 285 },
        { name: "American Airlines", price: 308 },
        { name: "Delta Air Lines", price: 331, note: "Most expensive" },
      ],
      strategy: "Book ~30 days out for best value",
      reason:
        "Book around 30 days before departure for the strongest balance of price and timing.",
    },
    {
      route: "BOS-DFW",
      tag: "Wait for sweet spot",
      bestWindow: "30 days",
      bestWindowDays: 30,
      bestPrice: 277,
      d90: 302,
      d30: 277,
      d10: 388,
      d1: 497,
      cheapestAirline: "Southwest Airlines",
      cheapestAirlinePrice: 244,
      airlines: [
        { name: "Southwest Airlines", price: 244, note: "Cheapest" },
        { name: "American Airlines", price: 268 },
        { name: "United Airlines", price: 291 },
        { name: "Delta Air Lines", price: 315, note: "Most expensive" },
      ],
      strategy: "Book ~30 days out for best value",
      reason:
        "Prices are lower at the 30-day window than both early and late booking periods.",
    },
    {
      route: "LAX-NYC",
      tag: "Book 30 days out",
      bestWindow: "30 days",
      bestWindowDays: 30,
      bestPrice: 362,
      d90: 380,
      d30: 362,
      d10: 490,
      d1: 664,
      cheapestAirline: "JetBlue Airways",
      cheapestAirlinePrice: 321,
      airlines: [
        { name: "JetBlue Airways", price: 321, note: "Cheapest" },
        { name: "American Airlines", price: 348 },
        { name: "United Airlines", price: 376 },
        { name: "Delta Air Lines", price: 401, note: "Most expensive" },
      ],
      strategy: "Book 30 days out",
      reason: "The model shows a clear upward jump after the 30-day booking window.",
    },
    {
      route: "ORD-PHX",
      tag: "Wait for sweet spot",
      bestWindow: "30 days",
      bestWindowDays: 30,
      bestPrice: 199,
      d90: 216,
      d30: 199,
      d10: 272,
      d1: 371,
      cheapestAirline: "Frontier Airlines",
      cheapestAirlinePrice: 168,
      airlines: [
        { name: "Frontier Airlines", price: 168, note: "Cheapest" },
        { name: "Southwest Airlines", price: 181 },
        { name: "American Airlines", price: 205 },
        { name: "United Airlines", price: 226, note: "Most expensive" },
      ],
      strategy: "Book ~30 days out for best value",
      reason:
        "This route stays reasonable early, but the best value still appears around 30 days out.",
    },
    {
      route: "SEA-ATL",
      tag: "Book ~30 days out",
      bestWindow: "30 days",
      bestWindowDays: 30,
      bestPrice: 310,
      d90: 338,
      d30: 310,
      d10: 428,
      d1: 584,
      cheapestAirline: "American Airlines",
      cheapestAirlinePrice: 288,
      airlines: [
        { name: "American Airlines", price: 288, note: "Cheapest" },
        { name: "United Airlines", price: 304 },
        { name: "Delta Air Lines", price: 329 },
        { name: "Alaska Airlines", price: 351, note: "Most expensive" },
      ],
      strategy: "Book ~30 days out",
      reason: "Waiting too long is expensive here, with a strong late-booking spike.",
    },
    {
      route: "DEN-LAX",
      tag: "Book ~30 days out",
      bestWindow: "30 days",
      bestWindowDays: 30,
      bestPrice: 181,
      d90: 196,
      d30: 181,
      d10: 248,
      d1: 336,
      cheapestAirline: "Frontier Airlines",
      cheapestAirlinePrice: 145,
      airlines: [
        { name: "Frontier Airlines", price: 145, note: "Cheapest" },
        { name: "Southwest Airlines", price: 168 },
        { name: "United Airlines", price: 187 },
        { name: "JetBlue Airways", price: 201, note: "Most expensive" },
      ],
      strategy: "Book ~30 days out",
      reason:
        "This is a lower-fare route, but last-minute booking still erodes savings fast.",
    },
  ];

  const [selectedRoute, setSelectedRoute] = useState(routes[0].route);
  const selected = useMemo(
    () => routes.find((item) => item.route === selectedRoute) || routes[0],
    [selectedRoute]
  );

  const maxPrice = Math.max(selected.d90, selected.d30, selected.d10, selected.d1);
  const savingsVsLastMinute = selected.d1 - selected.bestPrice;

  const windowBars = [
    { label: "90 days before", value: selected.d90, color: "bg-emerald-500", key: 90 },
    { label: "30 days before", value: selected.d30, color: "bg-blue-500", key: 30 },
    { label: "10 days before", value: selected.d10, color: "bg-amber-500", key: 10 },
    { label: "1 day before", value: selected.d1, color: "bg-rose-500", key: 1 },
  ];

  const formatMoney = (value) => `$${value}`;

  const cardClass =
    "rounded-[28px] border border-slate-200/80 bg-white p-6 shadow-[0_10px_30px_rgba(15,23,42,0.05)]";

  const sectionLabelClass =
    "inline-flex items-center gap-2 rounded-full border border-sky-100 bg-sky-50 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-sky-700";

  return (
    <div className="min-h-screen bg-[linear-gradient(180deg,#f8fbff_0%,#f3f7fb_100%)] text-slate-900">
      <div className="mx-auto max-w-7xl px-5 py-8 md:px-8 md:py-10">
        <div className="space-y-6">
          <header className="relative overflow-hidden rounded-[32px] border border-slate-200/80 bg-white p-6 shadow-[0_12px_40px_rgba(15,23,42,0.06)] md:p-7">
            <div className="pointer-events-none absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-sky-500 via-blue-500 to-cyan-400" />
            <div className="pointer-events-none absolute -right-10 -top-10 h-40 w-40 rounded-full bg-sky-100/70 blur-3xl" />
            <div className="flex flex-col gap-5 xl:flex-row xl:items-center xl:justify-between">
              <div className="flex items-start gap-4">
                <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-sky-500 to-blue-600 text-white shadow-sm">
                  <Plane className="h-7 w-7" />
                </div>
                <div>
                  <div className="flex flex-wrap items-center gap-3">
                    <h1 className="text-3xl font-semibold tracking-tight text-slate-900 md:text-4xl">
                      Airfare Intelligence System
                    </h1>
                    <span className="rounded-xl bg-emerald-500 px-4 py-2 text-sm font-semibold uppercase tracking-wide text-white shadow-sm">
                      FIFA World Cup 2026
                    </span>
                  </div>
                  <p className="mt-3 text-base text-slate-600">
                    ML-predicted prices · 4 booking windows · Route-level recommendations
                  </p>
                </div>
              </div>

              <div className="grid gap-3 sm:grid-cols-2">
                <div className="rounded-2xl bg-slate-50/90 px-4 py-3 border border-slate-200 min-w-[190px] backdrop-blur-sm">
                  <div className="flex items-center gap-2 text-sm font-medium text-slate-500">
                    <Info className="h-4 w-4 text-sky-600" /> Event Dates
                  </div>
                  <div className="mt-1 text-sm font-semibold text-slate-800">Jun 11 – Jul 19, 2026</div>
                </div>
                <div className="rounded-2xl bg-slate-50/90 px-4 py-3 border border-slate-200 min-w-[190px] backdrop-blur-sm">
                  <div className="flex items-center gap-2 text-sm font-medium text-slate-500">
                    <RefreshCw className="h-4 w-4 text-sky-600" /> Last Updated
                  </div>
                  <div className="mt-1 text-sm font-semibold text-slate-800">May 13, 2025 · 10:30 AM</div>
                </div>
              </div>
            </div>
          </header>

          <section className="rounded-3xl border border-slate-200 bg-white p-4 shadow-sm">
            <div className="flex flex-wrap gap-3">
              {routes.map((item) => {
                const active = item.route === selected.route;
                return (
                  <button
                    key={item.route}
                    onClick={() => setSelectedRoute(item.route)}
                    className={`rounded-2xl border px-4 py-3 text-left transition ${
                      active
                        ? "border-blue-600 bg-gradient-to-r from-sky-500 to-blue-600 text-white shadow-sm"
                        : "border-slate-200 bg-white text-slate-700 hover:border-sky-200 hover:bg-sky-50/60"
                    }`}
                  >
                    <div className="flex items-center gap-2 text-lg font-semibold tracking-tight">
                      <Plane className="h-4 w-4" />
                      {item.route}
                    </div>
                  </button>
                );
              })}
            </div>
          </section>

          <section className="grid gap-4 xl:grid-cols-4">
            <div className={cardClass}>
              <div className={sectionLabelClass}>
                <Ticket className="h-4 w-4" /> Fare insight
              </div>
              <div className="mt-4 flex items-center gap-3 text-slate-500">
                <div className="rounded-2xl bg-emerald-50 p-3 text-emerald-600">
                  <BadgeDollarSign className="h-5 w-5" />
                </div>
                <span className="text-sm font-semibold uppercase tracking-wide">Best Price</span>
              </div>
              <div className="mt-5 text-5xl font-semibold tracking-tight text-emerald-600">
                {formatMoney(selected.bestPrice)}
              </div>
              <div className="mt-2 text-lg text-slate-500">at {selected.bestWindow.toLowerCase()} window</div>
            </div>

            <div className={cardClass}>
              <div className={sectionLabelClass}>
                <Clock3 className="h-4 w-4" /> Booking risk
              </div>
              <div className="mt-4 flex items-center gap-3 text-slate-500">
                <div className="rounded-2xl bg-rose-50 p-3 text-rose-600">
                  <Clock3 className="h-5 w-5" />
                </div>
                <span className="text-sm font-semibold uppercase tracking-wide">Last-Minute Price</span>
              </div>
              <div className="mt-5 text-5xl font-semibold tracking-tight text-rose-600">
                {formatMoney(selected.d1)}
              </div>
              <div className="mt-2 text-lg text-slate-500">1 day before event</div>
            </div>

            <div className={cardClass}>
              <div className={sectionLabelClass}>
                <Map className="h-4 w-4" /> Route opportunity
              </div>
              <div className="mt-4 flex items-center gap-3 text-slate-500">
                <div className="rounded-2xl bg-amber-50 p-3 text-amber-600">
                  <CalendarDays className="h-5 w-5" />
                </div>
                <span className="text-sm font-semibold uppercase tracking-wide">Savings vs Last-Min</span>
              </div>
              <div className="mt-5 text-5xl font-semibold tracking-tight text-amber-600">
                {formatMoney(savingsVsLastMinute)}
              </div>
              <div className="mt-2 text-lg text-slate-500">booking at best window</div>
            </div>

            <div className={cardClass}>
              <div className={sectionLabelClass}>
                <Plane className="h-4 w-4" /> Airline pick
              </div>
              <div className="mt-4 flex items-center gap-3 text-slate-500">
                <div className="rounded-2xl bg-blue-50 p-3 text-blue-600">
                  <Plane className="h-5 w-5" />
                </div>
                <span className="text-sm font-semibold uppercase tracking-wide">Cheapest Airline</span>
              </div>
              <div className="mt-5 text-3xl font-semibold tracking-tight text-blue-600">
                {selected.cheapestAirline}
              </div>
              <div className="mt-2 text-lg text-slate-500">
                {formatMoney(selected.cheapestAirlinePrice)} at best window
              </div>
            </div>
          </section>

          <section className="grid gap-4 xl:grid-cols-[1.05fr_1fr]">
            <div className={cardClass}>
              <div className="flex items-center justify-between gap-4">
                <div>
                  <div className={sectionLabelClass}>
                    <CalendarDays className="h-4 w-4" /> Fare curve
                  </div>
                  <div className="mt-3 text-3xl font-semibold tracking-tight text-slate-900">
                    Price by Booking Window
                  </div>
                </div>
              </div>
              <div className="mt-8 space-y-5">
                {windowBars.map((item) => {
                  const width = (item.value / maxPrice) * 100;
                  const isBest = item.key === selected.bestWindowDays;
                  return (
                    <div key={item.label} className="grid grid-cols-[150px_1fr_85px_auto] items-center gap-4">
                      <div className="text-lg font-medium text-slate-700">{item.label}</div>
                      <div className="h-4 overflow-hidden rounded-full bg-slate-100">
                        <div className={`h-full rounded-full ${item.color}`} style={{ width: `${width}%` }} />
                      </div>
                      <div className={`text-right text-2xl ${isBest ? "font-semibold text-blue-700" : "text-slate-800"}`}>
                        {formatMoney(item.value)}
                      </div>
                      <div>
                        {isBest ? (
                          <span className="rounded-xl bg-emerald-100 px-3 py-1 text-sm font-semibold text-emerald-700">
                            BEST
                          </span>
                        ) : null}
                      </div>
                    </div>
                  );
                })}
              </div>
              <p className="mt-8 text-sm text-slate-500">
                Prices are predicted average fares for the selected route.
              </p>
            </div>

            <div className={cardClass}>
              <div className="flex items-center justify-between gap-4">
                <div>
                  <div className={sectionLabelClass}>
                    <Plane className="h-4 w-4" /> Airline comparison
                  </div>
                  <div className="mt-3 text-3xl font-semibold tracking-tight text-slate-900">
                    Airline Prices at Best Window
                  </div>
                </div>
                <div className="text-sm text-slate-500">({selected.bestWindow.toLowerCase()} before)</div>
              </div>

              <div className="mt-6 overflow-hidden rounded-2xl border border-slate-200">
                <table className="min-w-full text-left">
                  <thead className="bg-slate-50 text-slate-500">
                    <tr>
                      <th className="px-4 py-3 text-sm font-semibold">Airline Name</th>
                      <th className="px-4 py-3 text-sm font-semibold">Price</th>
                      <th className="px-4 py-3 text-sm font-semibold">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selected.airlines.map((airline) => (
                      <tr key={airline.name} className="border-t border-slate-200 bg-white">
                        <td className="px-4 py-4 text-lg font-medium text-slate-800">{airline.name}</td>
                        <td className="px-4 py-4 text-lg font-semibold text-slate-800">{formatMoney(airline.price)}</td>
                        <td className="px-4 py-4">
                          {airline.note ? (
                            <span
                              className={`inline-flex rounded-xl px-3 py-1 text-sm font-semibold ${
                                airline.note === "Cheapest"
                                  ? "bg-emerald-100 text-emerald-700"
                                  : "bg-rose-100 text-rose-700"
                              }`}
                            >
                              {airline.note}
                            </span>
                          ) : (
                            <span className="text-sm text-slate-400">—</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </section>

          <section className="relative overflow-hidden rounded-[32px] border border-sky-100 bg-[linear-gradient(135deg,#eff7ff_0%,#eef4ff_48%,#f8fbff_100%)] px-7 py-7 shadow-[0_12px_30px_rgba(59,130,246,0.08)]">
            <div className="pointer-events-none absolute right-8 top-8 hidden text-sky-100 lg:block">
              <Plane className="h-40 w-40 rotate-12" strokeWidth={1.2} />
            </div>
            <div className="max-w-3xl">
              <div className="flex items-center gap-3 text-blue-600">
                <div className="rounded-2xl bg-white p-3 shadow-sm">
                  <Lightbulb className="h-6 w-6" />
                </div>
                <span className="text-sm font-semibold uppercase tracking-wide">Recommendation</span>
              </div>
              <div className="mt-4 text-4xl font-semibold tracking-tight text-slate-900">
                {selected.route} — {selected.tag}
              </div>
              <p className="mt-4 text-xl leading-8 text-slate-700">
                {selected.reason} Predicted best price: <span className="font-semibold text-slate-900">{formatMoney(selected.bestPrice)}</span> at the {selected.bestWindow.toLowerCase()} window. Cheapest airline: <span className="font-semibold text-slate-900">{selected.cheapestAirline}</span>.
              </p>
              <div className="mt-5 inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-white/80 px-4 py-2 text-sm font-semibold text-emerald-700">
                <ShieldCheck className="h-4 w-4" /> Recommended booking strategy: {selected.strategy}
              </div>
            </div>
            <div className="pointer-events-none absolute -right-10 -bottom-10 h-44 w-44 rounded-full bg-blue-100 blur-2xl" />
          </section>

          <section className={cardClass}>
            <div>
              <div className={sectionLabelClass}>
                <Map className="h-4 w-4" /> Route board
              </div>
              <div className="mt-3 mb-5 text-3xl font-semibold tracking-tight text-slate-900">
                All Routes — Recommendation Matrix
              </div>
            </div>
            <div className="overflow-x-auto rounded-2xl border border-slate-200">
              <table className="min-w-full text-left text-sm">
                <thead className="bg-slate-50 text-slate-500">
                  <tr>
                    <th className="px-4 py-4 font-semibold">Route</th>
                    <th className="px-4 py-4 font-semibold">Best Window</th>
                    <th className="px-4 py-4 font-semibold">Best Price</th>
                    <th className="px-4 py-4 font-semibold">90-Day Price</th>
                    <th className="px-4 py-4 font-semibold">30-Day Price</th>
                    <th className="px-4 py-4 font-semibold">10-Day Price</th>
                    <th className="px-4 py-4 font-semibold">1-Day Price</th>
                    <th className="px-4 py-4 font-semibold">Cheapest Airline (at Best Window)</th>
                    <th className="px-4 py-4 font-semibold">Strategy</th>
                  </tr>
                </thead>
                <tbody>
                  {routes.map((item) => (
                    <tr
                      key={item.route}
                      onClick={() => setSelectedRoute(item.route)}
                      className={`cursor-pointer border-t border-slate-200 transition hover:bg-slate-50 ${
                        item.route === selected.route ? "bg-blue-50/70" : "bg-white"
                      }`}
                    >
                      <td className="px-4 py-4 font-semibold text-blue-600">{item.route}</td>
                      <td className="px-4 py-4">
                        <span className="rounded-xl bg-emerald-100 px-3 py-1 text-sm font-semibold text-emerald-700">
                          {item.bestWindow}
                        </span>
                      </td>
                      <td className="px-4 py-4 text-xl font-semibold text-emerald-600">{formatMoney(item.bestPrice)}</td>
                      <td className="px-4 py-4 text-slate-600">{formatMoney(item.d90)}</td>
                      <td className="px-4 py-4 font-semibold text-slate-900">{formatMoney(item.d30)}</td>
                      <td className="px-4 py-4 text-amber-600 font-semibold">{formatMoney(item.d10)}</td>
                      <td className="px-4 py-4 text-rose-600 font-semibold">{formatMoney(item.d1)}</td>
                      <td className="px-4 py-4 text-slate-700">
                        {item.cheapestAirline} <span className="font-semibold">({formatMoney(item.cheapestAirlinePrice)})</span>
                      </td>
                      <td className="px-4 py-4 font-medium text-teal-700">{item.strategy}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <footer className="flex flex-col gap-3 rounded-[28px] border border-slate-200/80 bg-white px-5 py-4 text-sm text-slate-500 shadow-[0_8px_24px_rgba(15,23,42,0.04)] md:flex-row md:items-center md:justify-between">
            <div className="flex items-center gap-2">
              <Info className="h-4 w-4" /> Prices are ML-predicted and may change. Check with airlines before booking.
            </div>
            <div className="flex items-center gap-2">
              <RefreshCw className="h-4 w-4" /> Data updated: May 13, 2025 · 10:30 AM
            </div>
          </footer>
        </div>
      </div>
    </div>
  );
}
