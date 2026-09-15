# Latest Agent Handoff

Handoff version: 0004
Last updated: 2026-09-15
Status: SFDHMC editable LAVI draft prepared for scope/pricing review; PDF not requested yet.

## Current Task
Prepare LAVI Technologies quotations for Saint Francis Doctors' Hospital & Medical Center, Cagayan de Oro: IP PABX and ITC PA. James requested an editable draft before PDF production.

## Authoritative Scope
- James's latest instruction sets PA coverage to floors 4–8: approximately 10 speakers each, plus 2 roof speakers; provisional total 52.
- IP alternative: 50 indoor IP speakers, 2 weatherproof outdoor IP speakers, 5 TP-Link 24-port PoE switches (one per floor).
- Analog alternative: 50 indoor analog speakers, 2 weatherproof roof speakers, one ITC IP amplifier per floor (5 total).
- Speakers and PA amplifiers are ITC. Existing cabling is assumed installed.
- No telephone count, IP PABX capacity, ITC supplier rates, VAT treatment or project commercial terms has been approved.
- Do not use prior MAB/Auveo or other-project rates as ITC/SFDHMC prices.

## Draft Decisions, Not Yet Approved
- IP switch specification proposed: 24 PoE+ ports, 250W budget; roof points served by 8th-floor switch.
- Analog sizing proposed: four 120W IP amplifiers for floors 4–7; one 240W for floor 8 plus roof. Basis: 10 x 6W = 60W per floor; 8th floor plus 2 x 30W roof = 120W connected load.
- Analog roof shares 8th-floor paging zone. IP roof can be a separate paging group.
- Both alternatives include one compatible ITC controller/server/software package and one IP paging microphone, installation, configuration and turnover.
- Availability of inter-floor network, network ports for head-end/amplifiers, equipment cabinets and AC power is a stated draft assumption.
- All prices, totals, tax and commercial terms are TBC. IP PABX central unit/handsets/configuration remain an explicit provisional section.
- Final ITC model compatibility and actual speaker cable/data topology require confirmation before finalization.

## Sources and Outputs
- Source PDFs supplied by James: Floor Plan - SFDHMC (13 pages), PAGA System - SFDHMC (10 pages).
- Earlier review found floor naming/layout differences; James's new floor coverage controls this draft.
- Draft: `work/sfdhmc-communications/2026-09-15-draft-01.md`.
- Saved user artifact: `LAVI_SFDHMC_IP_PABX_PA_Draft_01.md`, Library ID `libfile_41025181ed64819185c1c86acc61ecfa`.
- Delivery: one editable standard writing block; PDF not generated.
- Use locked `LAVI-QUOTATION-2026.2` engine for eventual PDF. Do not use Lifes Awesome profile.

## Verification
- Read AGENTS.md, prior LATEST.md, engine manifest and approved sample.
- Verified 5 x 10 + 2 = 52 speakers, 5 switches for IP, 4 + 1 = 5 analog IP amplifiers.
- Reviewed ITC manufacturer references for PoE speakers, 100V IP amplifiers and paging control; TP-Link reference confirms 24 PoE+ ports and 250W.
- Technical references: https://www.itctech.com.cn/pro/index/art/2965.html ; https://www.itctech.com.cn/pro/index/art/3678.html ; https://www.itctech.com.cn/pro/index/art/1718.html ; https://www.omadanetworks.com/ph/business-networking/omada-switch-access/tl-sg2428p/
- No approved selling prices or final package compatibility established. No PDF QA claimed.

## Next Steps
1. Apply James's edits to this draft.
2. Complete supplier-backed ITC rates and selling prices, telephone schedule and capacity, selected PA option, tax and commercial terms.
3. Confirm roof zoning, existing cable suitability, network/power/cabinet assumptions and final ITC package compatibility.
4. Generate PDF only when James requests it, through locked engine with required content and visual QA.

## Earlier Unfinished Work
The prior MAB/Lifes Awesome template review handoff is preserved in `.agents/handoffs/2026-09-15-previous-mab-template-review.md`. Its status was not changed by this task.
