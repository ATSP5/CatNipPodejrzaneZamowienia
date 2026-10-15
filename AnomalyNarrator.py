from typing import List

from AnomalyReport import AnomalyReport
from PlnFormat import PlnFormat


class AnomalyNarrator:
    """Zamienia wynik przeglądu w kilka zdań: ile zamówień sprawdzić, dlaczego i kto za nimi stoi."""

    def __init__(self, formatter: PlnFormat):
        self.formatter = formatter

    def narrator(self) -> "AnomalyNarrator":
        return self

    def headline(self, report: AnomalyReport) -> str:
        f = self.formatter
        return "%s zamówień przejrzanych w %s s → %d do sprawdzenia (%s z %s obrotu)." % (
            f.num(report.total_orders), f.num(report.seconds, 1), report.flagged_count,
            f.short_zl(report.flagged_value), f.short_zl(report.total_value))

    def findings(self, report: AnomalyReport) -> List[str]:
        f = self.formatter
        counts = {row["Reguła"]: row["Zamówienia"] for row in report.rule_rows}
        lines = []
        discounts = counts.get("Nietypowy rabat", 0)
        if discounts:
            line = "%d ma nietypowy rabat" % discounts
            if report.rep_rows and report.rep_rows[0]["Udział w podejrzanych %"] >= 30:
                top = report.rep_rows[0]
                line += " — %d podejrzanych cen i rabatów to handlowiec %s, który obsługuje tylko %s zamówień" % (
                    top["Podejrzane ceny/rabaty"], top["Handlowiec"], f.pct(top["Udział we wszystkich zamówieniach %"]))
            lines.append(line + ".")
        below = counts.get("Cena poniżej kosztu", 0)
        if below:
            loss = float(report.flagged["Strata"].sum())
            lines.append("%d sprzedano poniżej kosztu (strata %s)." % (below, f.zl(loss)))
        for rule, text in (("Cena odbiega od cennika", "%d ma cenę daleko od cennika."),
                           ("Nietypowa ilość", "%d ma ilość wielokrotnie większą niż zwykle dla tego produktu."),
                           ("Nietypowa pora", "%d złożono w nocy albo w niedzielę."),
                           ("Możliwy duplikat", "%d to prawdopodobne duplikaty (to samo zamówienie w ciągu kilku minut).")):
            if counts.get(rule, 0):
                lines.append(text % counts[rule])
        for group in report.similar_groups:
            rows = [r for r in report.similar_rows if r["Klient"].split(" ")[0] in group]
            since = {str(r["Klient od"]) for r in rows}
            reps = {str(r["Handlowiec"]) for r in rows}
            lines.append("%d klientów (%s) ma niemal identyczny wzorzec zamówień%s%s." % (
                len(group), ", ".join(group), "; wszyscy od %s" % since.pop() if len(since) == 1 else "",
                ", ten sam handlowiec %s" % reps.pop() if len(reps) == 1 else ""))
        if report.behaviour_rows:
            lines.append("%d klientów w ostatnim miesiącu zamawia kilka razy więcej niż zwykle: %s." % (
                len(report.behaviour_rows),
                ", ".join("%s (×%s)" % (r["Klient"].split(" ")[0], f.num(r["Krotność"], 1)) for r in report.behaviour_rows)))
        return lines
