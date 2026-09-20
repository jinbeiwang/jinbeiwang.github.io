---
title: "Chained kit replacement with the SAS hash object"
summary: "Resolving a replacement chain of unknown depth in one pass of a DATA step: why an in-memory hash is the only structure that fits this shape of problem, what the step guarantees, and what it does when the extract is not clean. A self-contained Base SAS check ships with the note — one fixture, eleven assertions."
date: 2026-09-20
category: SAS patterns
tags: [SAS, Hash, kit replacement, SDTM/ADaM]
lang: en
---

<div class="meta-row">
    <span><b>Source</b> &nbsp;the IRT kit-derivation step of a de-identified SDTM EC program; no study data</span>
    <span><b>Status</b> &nbsp;static analysis — the listings are the program as it stands, and the shipped check has not been run in a SAS session</span>
</div>


<div class="box note" style="margin-top:26px;">
  <span class="t">Scope and de-identification</span>
  <p class="small">Study identifiers, library names, paths and program headers have been removed or replaced by placeholders. The listings are self-contained and are referred to by step and by marker rather than by line number, so they can be lifted into another program without editing references. The check that accompanies the note is synthetic in the same way: it reads no study data.</p>
  <p class="small">This is the kit-replacement derivation only — the split of the IRT feed, the chain walk, the collapse to one record per subject and visit, and the join back to the clinical records. It is not a general hash tutorial and not a full SDTM EC mapping specification.</p>
</div>


<!-- ============================================================ -->
<h2><span class="n">1</span>The problem the code solves</h2>
<p class="lede">A linked list stored as rows, and the identifiers that have to come out of the far end of it.</p>

<p><code>ECREFID</code>, <code>ECLOT</code> and <code>BATCHNUM</code> must carry the <em>final</em> kit of a visit, not the kit recorded at that visit, because a kit can be replaced one or more times before or during administration. The IRT extract holds both facts in one table: the kit used, and the kit it was replaced by.</p>

<p>That makes the input a singly linked list. Each row is a node, <code>kitnumrp</code> is the pointer, and the terminal node is the row whose pointer is missing. Walking it needs random access to the node table from inside a loop, which is what a hash object provides and a merge does not.</p>

<h3>1.1 Terms</h3>
<table>
  <thead><tr><th style="width:180px;">Variable</th><th>Role in the pattern</th></tr></thead>
  <tbody>
    <tr><td><code>scn_num</code></td><td>Subject identifier. Half of the hash key, and the join key back to <code>SUBJID</code>.</td></tr>
    <tr><td><code>vis_type</code></td><td>Visit label. Drives the split, and is the join key back to <code>VISIT</code>.</td></tr>
    <tr><td><code>kit_tyds</code></td><td>Kit type. Part of the collapse key; a visit may legitimately carry several kit types.</td></tr>
    <tr><td><code>kit_num</code></td><td>Kit number. The second half of the hash key, and the value the walk rewrites.</td></tr>
    <tr><td><code>kitnumrp</code></td><td>&ldquo;Kit number replacement&rdquo;: the kit that this kit was replaced by, missing on a terminal kit. <b>This is the pointer.</b></td></tr>
    <tr><td><code>lot_num</code>, <code>btch_num</code></td><td>Lot and batch of the row's kit. Carried as hash payload so the terminal hop supplies them.</td></tr>
  </tbody>
</table>

<div class="box takeaway"><span class="t">The shape of the problem</span><p>Three properties are needed at once: re-probe the same table with a <em>different</em> key inside one observation, leave the driving table in its own order, and cope with a chain depth that is unknown until the data is read. A merge or a join satisfies none of the three.</p></div>

<figure>
<svg viewBox="0 0 680 296" role="img" aria-label="Left: the IRT feed is split into visit-level rows and replacement rows; the replacement rows are deduplicated and loaded into a hash object keyed on subject and kit number. Below: a base row is walked through a probe loop until the chain reaches a terminal kit.">
    <text x="16" y="20" font-size="10.5" font-weight="700" fill="#8b949e" letter-spacing="0.1em">PREPARE</text>
    <rect x="16" y="34" width="132" height="54" rx="5" fill="#ffffff" stroke="#c9d2dc"/>
    <text x="82" y="56" text-anchor="middle" font-size="12.5" font-weight="700" fill="#17181a">IRT feed</text>
    <text x="82" y="73" text-anchor="middle" font-size="10.5" fill="#5b6570">one row per kit event</text>
    <line x1="148" y1="61" x2="170" y2="61" stroke="#1b4f8a" stroke-width="1.4"/>
    <polygon points="170,61 162,57.5 162,64.5" fill="#1b4f8a"/>
    <text x="159" y="52" text-anchor="middle" font-size="9.5" fill="#5b6570">split</text>
    <rect x="176" y="34" width="178" height="25" rx="4" fill="#f7f9fb" stroke="#c9d2dc"/>
    <text x="186" y="51" font-size="11" font-weight="600" fill="#17181a">irt_base</text>
    <text x="238" y="51" font-size="10" fill="#5b6570">visit-level, the driving SET</text>
    <rect x="176" y="66" width="178" height="25" rx="4" fill="#f7f9fb" stroke="#c9d2dc"/>
    <text x="186" y="83" font-size="11" font-weight="600" fill="#17181a">irt_rp</text>
    <text x="222" y="83" font-size="10" fill="#5b6570">replacement rows, nodupkey</text>
    <line x1="354" y1="78" x2="382" y2="78" stroke="#1b4f8a" stroke-width="1.4"/>
    <polygon points="382,78 374,74.5 374,81.5" fill="#1b4f8a"/>
    <text x="368" y="70" text-anchor="middle" font-size="9.5" fill="#5b6570">load</text>
    <rect x="386" y="30" width="278" height="102" rx="5" fill="#ffffff" stroke="#1b4f8a" stroke-width="1.5"/>
    <text x="398" y="49" font-size="12" font-weight="700" fill="#1b4f8a">hash object h</text>
    <text x="398" y="67" font-size="10.5" fill="#17181a">key &#160;&#160;(scn_num, kit_num)</text>
    <text x="398" y="83" font-size="10.5" fill="#17181a">data &#160;(kitnumrp, lot_num, btch_num)</text>
    <text x="398" y="101" font-size="10" fill="#5b6570">built once from irt_rp; a repeated key stops the</text>
    <text x="398" y="116" font-size="10" fill="#5b6570">load rather than being resolved silently</text>
    <text x="16" y="158" font-size="10.5" font-weight="700" fill="#8b949e" letter-spacing="0.1em">WALK</text>
    <rect x="16" y="172" width="150" height="72" rx="5" fill="#ffffff" stroke="#c9d2dc"/>
    <text x="28" y="191" font-size="11.5" font-weight="700" fill="#17181a">base row</text>
    <text x="28" y="208" font-size="10.5" fill="#5b6570">kit_num = 1001</text>
    <text x="28" y="223" font-size="10.5" fill="#17181a">kitnumrp = 1002</text>
    <text x="28" y="238" font-size="10.5" fill="#5b6570">lot_num = LOT-A</text>
    <line x1="166" y1="208" x2="188" y2="208" stroke="#1b4f8a" stroke-width="1.4"/>
    <polygon points="188,208 180,204.5 180,211.5" fill="#1b4f8a"/>
    <rect x="192" y="170" width="252" height="104" rx="5" fill="#f7f9fb" stroke="#b9c4cf" stroke-dasharray="4 3"/>
    <text x="204" y="186" font-size="10" font-weight="700" fill="#5b6570" letter-spacing="0.06em">PROBE LOOP  do i = 1 to 100</text>
    <rect x="204" y="194" width="228" height="22" rx="3" fill="#ffffff" stroke="#dfe5ea"/>
    <text x="212" y="209" font-size="10.5" fill="#17181a">find(1002) &#8594; kitnumrp = 1003</text>
    <rect x="204" y="219" width="228" height="22" rx="3" fill="#ffffff" stroke="#dfe5ea"/>
    <text x="212" y="234" font-size="10.5" fill="#17181a">find(1003) &#8594; kitnumrp = 1004</text>
    <rect x="204" y="244" width="228" height="22" rx="3" fill="#ffffff" stroke="#dfe5ea"/>
    <text x="212" y="259" font-size="10.5" fill="#17181a">find(1004) &#8594; kitnumrp = . &#160;exit</text>
    <line x1="444" y1="170" x2="444" y2="136" stroke="#1b4f8a" stroke-width="1.2" stroke-dasharray="3 3"/>
    <polygon points="444,136 440.5,144 447.5,144" fill="#1b4f8a"/>
    <text x="452" y="162" font-size="9.5" fill="#1b4f8a">re-probe</text>
    <line x1="444" y1="208" x2="470" y2="208" stroke="#1b4f8a" stroke-width="1.4"/>
    <polygon points="470,208 462,204.5 462,211.5" fill="#1b4f8a"/>
    <rect x="474" y="172" width="190" height="72" rx="5" fill="#f0f7f4" stroke="#0f7b5f" stroke-width="1.5"/>
    <text x="486" y="191" font-size="11.5" font-weight="700" fill="#0f7b5f">terminal kit</text>
    <text x="486" y="208" font-size="10.5" fill="#17181a">kit_num = 1004</text>
    <text x="486" y="223" font-size="10.5" fill="#17181a">ECLOT = LOT-D</text>
    <text x="486" y="238" font-size="10.5" fill="#17181a">BATCHNUM = B04</text>
    <text x="16" y="288" font-size="10" fill="#8b949e">A probe that misses does not change the payload; a probe that hits rewrites the pointer, so the next iteration moves one link further.</text>
</svg>
<figcaption><b>Figure 1 |</b> The feed is split in two, the small replacement table is deduplicated and loaded into a hash object, and the large visit-level table is then streamed past it once. Each successful probe rewrites <code>kitnumrp</code> and the lot/batch payload in the PDV, which is what advances the walk.</figcaption>
</figure>


<!-- ============================================================ -->
<h2><span class="n">2</span>Hash essentials</h2>
<p class="lede">The minimum that has to be understood before the code in section 3 reads as obvious.</p>

<h3>2.1 Skeleton</h3>

<pre><code><span class="kw">if</span> _n_ = 1 <span class="kw">then do</span>;                                     <span class="mk">(1)</span>
   <span class="kw">declare hash</span> h(dataset: "irt_rp",
                                             duplicate: "error");          <span class="mk">(2)</span>
   h.definekey("scn_num","kit_num");                  <span class="mk">(3)</span>
   h.definedata("kitnumrp","lot_num","btch_num");     <span class="mk">(4)</span>
   h.definedone();                                    <span class="mk">(5)</span>
<span class="kw">end</span>;
...
rc = h.find();                                        <span class="mk">(6)</span></code></pre>

<ol>
  <li>The guard. <code>declare</code> is a compile-time statement, but the object is created and the table read when the step executes: without <code>if _n_ = 1</code> both are redone on every iteration.</li>
  <li>Declare, and point at the source table. A data set name in the <code>dataset:</code> tag is loaded at <code>definedone()</code>, and the rule for a repeated key belongs here too — Listing&nbsp;3 depends on it.</li>
  <li>The key: the variables that form the address. <strong>Define the key first</strong>; lookup compares the <em>current</em> values of these PDV variables.</li>
  <li>The data: the payload a successful probe writes back. A variable may be both key and data, and then matches by value and is overwritten as payload.</li>
  <li>Ends the definition and triggers the load. Every name in <code>definekey</code> or <code>definedata</code> must exist in the PDV by this point.</li>
  <li>The probe. With no arguments it works on the PDV variables of steps 3 and 4; a driver can be passed with the <code>key:</code> tag.</li>
</ol>

<h3>2.2 The one design decision that carries the whole pattern</h3>
<p>In this program <code>kitnumrp</code> is declared as <em>data</em> even though it also drives the loop, and that is load-bearing. A successful <code>find()</code> writes the payload straight back into the PDV, so the loop control variable advances by itself, and the terminal hop's <code>lot_num</code> and <code>btch_num</code> arrive in the same write — which is what keeps <code>ECLOT</code> and <code>BATCHNUM</code> consistent with the terminal kit.</p>

<h3>2.3 Argument tags worth knowing</h3>
<table>
  <thead><tr><th style="width:210px;">Tag</th><th>Effect</th></tr></thead>
  <tbody>
    <tr><td><code>dataset: "name"</code></td><td>Loads the table at <code>definedone()</code>; data set options such as <code>where=</code> may be embedded in the string.</td></tr>
    <tr><td><code>duplicate: "replace" | "error"</code></td><td>The default keeps the <em>first</em> row for a repeated key and writes nothing to the log; <code>"replace"</code> keeps the last; <code>"error"</code> stops the load. <em class="ev">[doc]</em></td></tr>
    <tr><td><code>multidata: "yes"</code></td><td>Several payloads per key, walked with <code>find_next</code>. For a kit that legitimately has more than one replacement record.</td></tr>
    <tr><td><code>ordered: "yes"</code></td><td>Keeps the entries in key order, which an iterator requires.</td></tr>
  </tbody>
</table>

<h3>2.4 Methods used, and the ones to reach for next</h3>
<table>
  <thead><tr><th style="width:210px;">Method</th><th>Purpose</th></tr></thead>
  <tbody>
    <tr><td><code>definekey</code> / <code>definedata</code> / <code>definedone</code></td><td>Build the object. The order is fixed.</td></tr>
    <tr><td><code>find()</code></td><td>Look up the current key; on a hit, copy the payload into the PDV.</td></tr>
    <tr><td><code>check()</code></td><td>The same test without the copy, for an existence test where the old values must survive.</td></tr>
    <tr><td><code>add()</code> / <code>replace()</code> / <code>remove()</code></td><td>Maintain the object at run time instead of loading it from a table.</td></tr>
    <tr><td><code>num_items</code></td><td>Attribute, not a method: how many entries there are. Worth a line in the log as a load check.</td></tr>
  </tbody>
</table>

<div class="box finding"><span class="t">The return code is inverted</span><p><code>0</code> means success and a non-zero value means failure — the opposite of what most people expect. Assign the return code and test it: a failure whose code was <em>not</em> assigned writes an error to the log, while one that <em>was</em> assigned stays silent until you look. <em class="ev">[doc]</em></p></div>

<h3>2.5 Pitfalls</h3>
<table>
  <thead><tr><th style="width:230px;">Symptom</th><th>Cause and remedy</th></tr></thead>
  <tbody>
    <tr><td><code>NOTE: Variable X is uninitialized</code></td><td>The compiler cannot see the assignments the hash performs, so a key or data variable with no assignment anywhere in the step is reported. Give it a <code>length</code> and an initial assignment, or <code>call missing</code>.</td></tr>
    <tr><td>Extra columns in the output data set</td><td>Variables created for the hash live in the PDV and are written out with everything else. Add them to a <code>drop</code> unless they are deliverables.</td></tr>
    <tr><td>Silent wrong lookup, no message</td><td>A duplicate key was loaded and the first row won. Decide the rule and enforce it, or use <code>duplicate: "error"</code>.</td></tr>
    <tr><td>Every observation returns the same value</td><td>The key variable is not the one the <code>set</code> updates, or the driver was passed as a literal. Names resolve case-insensitively, so it is nearly always a wrong name rather than a wrong case.</td></tr>
  </tbody>
</table>

<div class="box takeaway"><span class="t">This section in one line</span><p>The payload of a probe <em>is</em> the loop's progress: declare <code>kitnumrp</code> as data and the walk advances without a single assignment of its own — but then the loop can only be stopped by the pointer, never by the index.</p></div>

<!-- ============================================================ -->
<h2><span class="n">3</span>Reading the code</h2>
<p class="lede">Five steps in the order they run: split the feed, reduce it to one row per kit, walk the chain, collapse the result back to one record per visit, and join it to the clinical records.</p>

<h3>Listing 1 — split the feed</h3>

<pre><code><span class="kw">data</span> irt_base irt_rp;                                        <span class="mk">(1)</span>
     <span class="kw">set</span> raw.irt_kit;                                        <span class="mk">(2)</span>
     vis_type = upcase(vis_type);
     <span class="kw">if</span> vis_type = "DISCONTINUE" <span class="kw">then</span> vis_type = "END OF TREATMENT";
     <span class="kw">keep</span> scn_num kit_tyds kit_num lot_num vis_type btch_num kitnumrp;
     <span class="kw">if</span> vis_type = "KIT REPLACEMENT" <span class="kw">then</span> <span class="kw">output</span> irt_rp;
     <span class="kw">else</span> <span class="kw">if</span> <span class="kw">not</span> <span class="kw">missing</span>(kit_tyds) <span class="kw">then</span> <span class="kw">output</span> irt_base;     <span class="mk">(3)</span>
<span class="kw">run</span>;</code></pre>
<ol>
  <li>Two output data sets from one pass; the explicit <code>output</code> statements mean each input row reaches at most one of them.</li>
  <li>The single IRT extract, holding both kinds of row, distinguished by <code>vis_type</code>.</li>
  <li>Case normalisation before the split, so the comparison below it is reliable, and a row with no kit type is dropped here. This is also the first half of the visit vocabulary the join needs; the clinical side keeps its own copy, outside this step.</li>
</ol>

<h3>Listing 2 — one row per kit, key and payload together</h3>

<pre><code><span class="cm">/* One row per kit for hash load. The BY list carries the payload as well, so a
   conflicting pair of replacement rows survives this step, and the load -- which
   is declared duplicate:"error" below -- refuses it instead of silently keeping
   the first row it happened to read. */</span>
<span class="kw">proc</span> <span class="kw">sort</span> <span class="kw">data</span> = irt_rp <span class="kw">nodupkey</span>;
     <span class="kw">by</span> scn_num kit_num kitnumrp lot_num btch_num;           <span class="mk">(4)</span>
<span class="kw">run</span>;</code></pre>
<ol start="4">
  <li>The deduplication and the guardrail are one decision. The <code>by</code> list is the hash key (<code>scn_num</code>, <code>kit_num</code>) <em>plus</em> the payload (<code>kitnumrp</code>, <code>lot_num</code>, <code>btch_num</code>), so it collapses only rows identical on all five fields — one event recorded twice — and leaves a genuine conflict for the load to refuse. §5.4 works through both, S17 and S14.</li>
</ol>

<h3>Listing 3 — walk the replacement chain to its terminal kit</h3>

<pre><code><span class="kw">data</span> irt_chase;
     <span class="kw">if</span> _n_ = 1 <span class="kw">then</span> <span class="kw">do</span>;
          <span class="kw">declare</span> <span class="kw">hash</span> h(dataset: "irt_rp", duplicate: "error");   <span class="cm">/* F3 */</span>   <span class="mk">(5)</span>
          h.<span class="kw">definekey</span>("scn_num","kit_num");
          h.<span class="kw">definedata</span>("kitnumrp","lot_num","btch_num");                     <span class="mk">(6)</span>
          h.<span class="kw">definedone</span>();
     <span class="kw">end</span>;
     <span class="kw">set</span> irt_base;                                                           <span class="mk">(7)</span>

     <span class="kw">length</span> chain_status $10;                                                <span class="mk">(8)</span>
     prev_kit = kit_num;                                            <span class="cm">/* F1 */</span>
     chain_status = '';

     <span class="kw">do</span> i = 1 <span class="kw">to</span> 100 <span class="kw">while</span> (<span class="kw">not</span> <span class="kw">missing</span>(kitnumrp));                          <span class="mk">(9)</span>
          kit_num = kitnumrp;                                                <span class="mk">(10)</span>
          rc = h.find();                                                     <span class="mk">(11)</span>
          <span class="kw">if</span> rc ne 0 <span class="kw">then</span> <span class="kw">do</span>;
               chain_status = 'DANGLING';
               kit_num = prev_kit;                                  <span class="cm">/* F1 */</span>
               <span class="kw">leave</span>;
          <span class="kw">end</span>;
          prev_kit = kit_num;
     <span class="kw">end</span>;

     <span class="kw">if</span> chain_status = '' <span class="kw">then</span>                                       <span class="cm">/* F2 */</span>
        chain_status = ifc(<span class="kw">missing</span>(kitnumrp), 'RESOLVED', 'UNRESOLVED');

     <span class="kw">if</span> chain_status ne 'RESOLVED' <span class="kw">then</span>
        <span class="kw">put</span> "WARNING: kit chain " chain_status= scn_num= vis_type= kit_tyds= kit_num=;

     <span class="kw">drop</span> i rc prev_kit;
<span class="kw">run</span>;</code></pre>
<ol start="5">
  <li>Declared and loaded once, from the deduplicated table, with the duplicate rule attached.</li>
  <li><code>kitnumrp</code> is payload, not just a pointer: a hit overwrites it with the next link, so the loop advances by the lookup itself, and the terminal hop's <code>lot_num</code> and <code>btch_num</code> arrive in the same write.</li>
  <li>The driving table, streamed in its own order; nothing has to be sorted by the lookup key.</li>
  <li>The status column, kept in the output so that a <code>proc freq</code> over it replaces grepping the log and a QC step can fail on it.</li>
  <li>Two termination conditions in one statement: a <code>while</code> test evaluated before every iteration including the first, and a hard budget of 100 probes.</li>
  <li>The pointer moves before the probe, so the row's own kit number is replaced by the recorded replacement.</li>
  <li>The probe. On a hit the payload lands in the PDV; on a miss nothing is written back, which is why the miss branch restores the previous kit itself.</li>
</ol>

<h3>Trace 1 — what one three-link walk does to the PDV</h3>
<p>The table follows one visit-level row whose kit <code>1001</code> was replaced by <code>1002</code>, then <code>1003</code>, then <code>1004</code>. It is a reading of the listing above, not a log extract: the step writes to the log only when a chain fails to resolve.</p>
<table>
  <thead><tr><th style="width:44px;">i</th><th>Before the probe</th><th>After <code>find()</code></th><th>Payload in the PDV</th></tr></thead>
  <tbody>
    <tr><td class="num">1</td><td class="num">kit_num = 1002</td><td class="num">rc = 0</td><td class="num">kitnumrp &#8594; 1003, lot LOT-B, batch B02</td></tr>
    <tr><td class="num">2</td><td class="num">kit_num = 1003</td><td class="num">rc = 0</td><td class="num">kitnumrp &#8594; 1004, lot LOT-C, batch B03</td></tr>
    <tr><td class="num">3</td><td class="num">kit_num = 1004</td><td class="num">rc = 0</td><td class="num">kitnumrp &#8594; missing, lot LOT-D, batch B04</td></tr>
  </tbody>
</table>
<p>After iteration 3 the <code>while</code> test fails and the row is left with <code>kit_num = 1004</code> and that kit's lot and batch, because one probe wrote all three back. Three probes for a three-link chain, and the first was aimed at the pointer on the base row rather than at the row's own kit number.</p>

<h3>Listing 4 — collapse to one record per visit</h3>

<pre><code><span class="kw">proc</span> <span class="kw">sort</span> <span class="kw">data</span> = irt_chase;
     <span class="kw">by</span> scn_num vis_type kit_tyds kit_num;                   <span class="mk">(12)</span>
<span class="kw">run</span>;

<span class="kw">data</span> irt_claps;
     <span class="kw">set</span> irt_chase;
     <span class="kw">by</span> scn_num vis_type kit_tyds kit_num;
     <span class="kw">length</span> refid $200;                                      <span class="mk">(13)</span>
     <span class="kw">retain</span> refid;
     <span class="kw">if</span> first.vis_type <span class="kw">then</span> refid = strip(<span class="kw">put</span>(kit_num, best.));
     <span class="kw">else</span> refid = strip(refid) || ', ' || strip(<span class="kw">put</span>(kit_num, best.));
     <span class="kw">if</span> last.vis_type;                                       <span class="mk">(14)</span>
<span class="kw">run</span>;</code></pre>
<ol start="12">
  <li>Sort order decides both the grouping and the order inside <code>refid</code>: kit type, then kit number — not the order the kits were administered in (F4).</li>
  <li>The accumulator, 200 characters, far more than a visit's handful of kits needs, so it does not truncate in practice (F4).</li>
  <li><code>last.vis_type</code> turns a visit's kit rows into one output row: the reference list, plus the lot and batch of the <em>last</em> row in sort order.</li>
</ol>

<h3>Listing 5 — back to the clinical records</h3>

<pre><code><span class="kw">proc</span> <span class="kw">sql</span>;
     <span class="kw">create</span> <span class="kw">table</span> ec_ext <span class="kw">as</span>
     <span class="kw">select</span> a.*, c.kit_tyds, c.kit_num, c.refid, c.lot_num, c.BTCH_NUM, c.vis_type
     <span class="kw">from</span> ec_dy <span class="kw">as</span> a <span class="kw">left</span> <span class="kw">join</span> irt_claps <span class="kw">as</span> c
     <span class="kw">on</span> a.subjid = c.scn_num <span class="kw">and</span> a.visit = c.vis_type;       <span class="mk">(15)</span>
<span class="kw">quit</span>;</code></pre>

<pre><code><span class="kw">data</span> ec_asgn;
     <span class="kw">length</span> domain $2 eclnkid $20 eclot ecrefid $200;
     <span class="kw">set</span> ec_ext;
     domain = 'EC';
     <span class="kw">if</span> ecstdtc ne '' <span class="kw">then</span>
     eclnkid = strip(compress(ecstdtc,"-:"))||'-'||upcase(substr(ectrt,1,1));
     <span class="kw">else</span> eclnkid = '';
     ecrefid = strip(refid);                                 <span class="mk">(16)</span>
     eclot   = strip(lot_num);
     BATCHNUM = strip(BTCH_NUM);
     <span class="kw">if</span> <span class="kw">not</span> <span class="kw">missing</span>(ecstdtc) <span class="kw">then</span> epoch = 'TREATMENT';
<span class="kw">run</span>;</code></pre>
<ol start="15">
  <li>A left join on subject and visit. The key is numeric on one side and character on the other in some extracts, and a type mismatch makes the join miss silently: the visit survives with missing kit information and nothing in the log says so.</li>
  <li>The three identifiers come straight from the collapsed record. <code>ECREFID</code> lists every kit the visit resolved to, while <code>ECLOT</code> and <code>BATCHNUM</code> come from the one row the collapse kept (F4).</li>
</ol>


<!-- ============================================================ -->
<h2><span class="n">4</span>Why a hash, and not a merge</h2>
<p class="lede">The comparison that decides the design, against the three properties this problem actually needs.</p>

<table>
  <thead>
    <tr>
      <th style="width:170px;">Approach</th>
      <th>Re-probe one observation's key against the same table</th>
      <th>Needs the driving table sorted by the lookup key</th>
      <th>Unknown depth, single pass</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>merge</code> / <code>set</code> with <code>by</code></td>
      <td><span class="pill bad">No</span> — one positional match per observation</td>
      <td><span class="pill bad">Yes</span> — both inputs must be sorted on the same keys</td>
      <td><span class="pill bad">No</span> — one hop per merge, so depth must be known</td>
    </tr>
    <tr>
      <td><code>proc sql</code> self-join</td>
      <td><span class="pill bad">No</span></td>
      <td><span class="pill ok">No</span></td>
      <td><span class="pill bad">No</span> — one hop per join, and SAS SQL has no recursive CTE</td>
    </tr>
    <tr>
      <td>Format or <code>put()</code> lookup</td>
      <td><span class="pill bad">No</span> — the value is fixed when the format is built</td>
      <td><span class="pill ok">No</span></td>
      <td><span class="pill bad">No</span> — single hop, and the format cannot be updated at run time</td>
    </tr>
    <tr>
      <td><code>set</code> with <code>key=</code> (index)</td>
      <td><span class="pill ok">Yes</span></td>
      <td><span class="pill ok">No</span></td>
      <td><span class="pill cav">Yes</span> — but every probe needs the index and costs more</td>
    </tr>
    <tr>
      <td>Hash object</td>
      <td><span class="pill ok">Yes</span></td>
      <td><span class="pill ok">No</span></td>
      <td><span class="pill ok">Yes</span></td>
    </tr>
  </tbody>
</table>

<div class="box takeaway"><span class="t">The decisive argument</span><p>The walk is a pointer chase of unknown length, and the number of hops is a property of the data rather than of the program: no fixed number of merges or joins can express it. A merge-based solution would have to keep joining until nothing changes, re-scanning and re-sorting on every pass, and it would destroy the subject-and-visit order the rest of the program depends on. The hash object is the only structure that lets a DATA step ask a question of a lookup table <em>from inside its own loop</em>.</p></div>

<p>Two smaller arguments point the same way. Sorting: the visit-level feed's natural order is by subject and visit, and the collapse depends on it, while a merge would impose its own sort and a second re-sort afterwards. Cost: the replacement table is small and read thousands of times, which is the case a hash is built for.</p>

<p><strong>When a merge is still the better tool.</strong> If the identifier needs one hop — a single <code>m:1</code> enrichment from a small reference table — a merge or a plain left join is shorter and easier for a second programmer to check. The hash earns its complexity only when the lookup repeats, with a key that changes during the observation. Either way, keep the <em>small</em> side in the hash: loading the visit-level feed would make memory grow with the study.</p>

<!-- ============================================================ -->
<h2><span class="n">5</span>Design and correctness</h2>
<p class="lede">What the step guarantees, what it does when the input is not clean, and what it does not cover.</p>

<div class="box note"><span class="t">How this section is argued</span><p class="small">Every claim below names the lines that carry it and the case that shows it. The cases are the fixture in §7.2, printed there as <code>kit_chain_check.sas</code> holds it, and the check asserts the result column of the matrix row by row. The expected results in §5.2 are therefore the specification the run tests, not a summary of a log: no SAS session was available where this note was written. §7.5 lists the three behaviours that only a real session settles.</p></div>

<h3>5.1 What the step guarantees</h3>
<table>
  <thead>
    <tr><th style="width:250px;">Guarantee</th><th>Where it comes from</th></tr>
  </thead>
  <tbody>
    <tr>
      <td><b>G1</b> &nbsp;The hash is loaded with one row per key, or the step does not run.</td>
      <td>The <code>by</code> list of the deduplication carries the key <em>and</em> the payload, so a conflict survives it (Listing&nbsp;2); the object is declared <code>duplicate: "error"</code>, so the conflict stops the load (Listing&nbsp;3, marker 5). S14 is that case.</td>
    </tr>
    <tr>
      <td><b>G2</b> &nbsp;A probe that hits advances the kit, the lot and the batch together; a probe that misses changes none of them.</td>
      <td>All three are hash payload, so one <code>find()</code> writes them back together, and the miss branch restores the previous kit (Listing&nbsp;3, markers 6 and 11). S02 and S06 show the two directions.</td>
    </tr>
    <tr>
      <td><b>G3</b> &nbsp;The walk cannot hang, and it cannot stop early in silence.</td>
      <td>The budget of 100 probes bounds the loop, and <code>chain_status</code> is computed after the loop from the pointer, which is missing only when the walk reached a terminal record. S03 and S07 are the two ends of that.</td>
    </tr>
    <tr>
      <td><b>G4</b> &nbsp;Every unresolved row is labelled and logged; no resolved row is.</td>
      <td><code>chain_status</code> is kept in the output and the <code>put</code> is gated on it. The check compares the status of every visit row, so an edit that quietly resolved a dangling row would fail it.</td>
    </tr>
  </tbody>
</table>

<h3>5.2 Scenario matrix</h3>
<p class="small">Each row names the case as the fixture records it — the kit numbers in the second column are the rows printed in §7.2 — and the check asserts the result column of every one of them. <em>Hops</em> is how many links the visit-level row walks, which is the number of <code>find()</code> calls it makes. <em>resolved</em> is the intended outcome; <em>flagged</em> means the row left with a status other than <code>RESOLVED</code> and one line in the log, so QC has to count it; <em>data issue</em> means the extract itself is wrong and the step's job is to refuse it.</p>
<table>
  <thead>
    <tr>
      <th style="width:38px;">ID</th>
      <th style="width:246px;">Case as tested</th>
      <th>Result — kit / lot / batch</th>
      <th style="width:46px;">Hops</th>
      <th style="width:88px;">Verdict</th>
    </tr>
  </thead>
  <tbody>
    <tr><td class="num">S01</td><td><span class="num">1001</span> terminal: no replacement recorded</td><td><span class="num">1001 / LOT-A / B01</span> — unchanged</td><td class="num">0</td><td><span class="pill ok">resolved</span></td></tr>
    <tr><td class="num">S02</td><td><span class="num">1001 &#8594; 1002</span>: one replacement</td><td><span class="num">1002 / LOT-B / B02</span></td><td class="num">1</td><td><span class="pill ok">resolved</span></td></tr>
    <tr><td class="num">S03</td><td><span class="num">1001 &#8594; 1002 &#8594; 1003 &#8594; 1004</span>: three replacements, the most the data has shown</td><td><span class="num">1004 / LOT-D / B04</span></td><td class="num">3</td><td><span class="pill ok">resolved</span></td></tr>
    <tr><td class="num">S05</td><td><span class="num">1001 &#8594; 9001</span>, and no row describes <span class="num">9001</span></td><td><span class="num">1001 / LOT-A / B01</span> — the kit the row started from, whole; one WARNING line</td><td class="num">1</td><td><span class="pill cav">flagged</span></td></tr>
    <tr><td class="num">S06</td><td><span class="num">1001 &#8594; 1002 &#8594; 1099</span>, and no row describes <span class="num">1099</span></td><td><span class="num">1002 / LOT-B / B02</span> — the kit from hop 2, with its own lot and batch; one WARNING line</td><td class="num">2</td><td><span class="pill cav">flagged</span></td></tr>
    <tr><td class="num">S07</td><td><span class="num">1001 &#8594; 1002 &#8594; 1003 &#8594; 1002</span>: a cycle</td><td><span class="num">1003 / LOT-C / B03</span> — well formed and wrong; one WARNING line</td><td class="num">100</td><td><span class="pill cav">flagged</span></td></tr>
    <tr><td class="num">S09</td><td>the row's own pointer is empty, although <span class="num">1001</span> was replaced</td><td><span class="num">1001 / LOT-A / B01</span> — unchanged; the key is never consulted</td><td class="num">0</td><td><span class="pill ok">resolved</span></td></tr>
    <tr><td class="num">S10</td><td><span class="num">1001 &#8594; 1002</span>, and the replacement table is empty</td><td><span class="num">1001 / LOT-A / B01</span> — restored, not the two halves of a pair; one WARNING line</td><td class="num">1</td><td><span class="pill cav">flagged</span></td></tr>
    <tr><td class="num">S11</td><td>the same kit number under two subjects, replaced differently</td><td><span class="num">subject 101 &#8594; 1002 / LOT-T1 / BT1; subject 202 &#8594; 1002 / LOT-T2 / BT2</span> — no cross-talk</td><td class="num">1</td><td><span class="pill ok">resolved</span></td></tr>
    <tr><td class="num">S12</td><td>the visit label arrives as <code>discontinue</code>, the replacement as <code>kit replacement</code></td><td><span class="num">1002 / LOT-B / B02</span> under <code>END OF TREATMENT</code> — normalised before the split</td><td class="num">1</td><td><span class="pill ok">resolved</span></td></tr>
    <tr><td class="num">S14</td><td>two rows claim kit <span class="num">1002</span> with different lots: a duplicate in the extract</td><td>load refused — <code>ERROR: Duplicate key (101, 1002)</code>, no output data set</td><td class="num">&mdash;</td><td><span class="pill cav">data issue</span></td></tr>
    <tr><td class="num">S17</td><td>kit <span class="num">1002</span> recorded twice, byte-identical</td><td><span class="num">1003 / LOT-C / B03</span> — three rows in, two keys loaded</td><td class="num">2</td><td><span class="pill ok">resolved</span></td></tr>
    <tr><td class="num">S15</td><td>2,000 subjects &times; 4 visits, three replacements each, every visit its own kit block</td><td>every row lands on its terminal kit, on a table of 24,000 replacement rows</td><td class="num">3</td><td><span class="pill ok">resolved</span></td></tr>
  </tbody>
</table>

<p class="small">The rows down to S11 are the walk. S12 is the split's normalisation, S14 and S17 are the deduplication in front of the load, and S15 is a volume check: cost is flat in chain depth and nothing exhausts the probe budget.</p>
<p class="small">Four cases that used to sit in this matrix are gone, all for the same reason — they were not about this step. Eight hops: S03 already shows the depth is open, and three replacements is the most the extract has shown. A kit whose pointer names itself: S07's cycle is the same failure. A row with no kit type (<code>SCREENING</code> in the raw IRT file) and a visit label the two sides of the join spell differently: both are settled before this step sees the data, one by the extract, the other by the clinical-side mapping. Testing them here would have made the matrix longer without telling a reader anything about the walk.</p>

<h3>5.3 When the chain does not resolve</h3>
<p>Two shapes of bad input reach the walk, and they fail differently. Neither is visible unless the status column is read: both leave an output that looks like any other row.</p>

<h4>The pointers, and what &ldquo;dangling&rdquo; means</h4>
<p>The extract carries one pointer column, <code>kitnumrp</code>: the kit that this kit was replaced by, missing on a terminal kit. Listing&nbsp;1 keeps it in both of its outputs. The step adds one pointer of its own, <code>prev_kit</code>, in the PDV, and drops it again with <code>rc</code> and the loop index, so the only pointer that survives into <code>irt_chase</code> is <code>kitnumrp</code> — kept deliberately, because the status test reads it. The join in Listing&nbsp;5 selects named columns, so no pointer reaches the SDTM variables at all: <code>ECREFID</code>, <code>ECLOT</code> and <code>BATCHNUM</code> carry the terminal kit, and nothing in the output records how many hops it took to get there.</p>
<p>A pointer is <em>dangling</em> when the kit it names has no row in the replacement table. That table is the only place a kit's successor is recorded, so such a pointer can never be followed and the walk stops one hop short of a terminal kit. It happens in two positions: on the first hop, where the visit row's own pointer names a kit the extract never described (S05: <span class="num">1001 &#8594; 9001</span>), and mid-chain, where a replacement row does (S06: <span class="num">1002 &#8594; 1099</span>). A dangling pointer is not a cycle: a cycle keeps resolving, it simply never arrives at a terminal kit (S07).</p>

<div class="box finding"><span class="t">F1 &nbsp;dangling pointer</span>
  <p><code>kit_num = kitnumrp;</code> runs before the probe, and a miss writes nothing back. Without the miss branch the row would leave with a kit number taken from the replacement record and a lot and batch taken from the row it replaced — a combination that exists in no record and that no <code>ECREFID</code> / <code>ECLOT</code> cross-check can reconcile. S05, S06 and S10 are that case, S10 with an empty table.</p>
  <p><strong>How the step handles it.</strong> <code>prev_kit</code> holds the kit the last successful probe landed on, and a miss restores it, so the three fields still describe one physical kit — the best available answer — and the row carries <code>DANGLING</code> and one <code>WARNING</code> line. The check asserts the restored triple for all three cases, which is what makes the restore a rule rather than a hope.</p>
</div>

<div class="box finding"><span class="t">F2 &nbsp;cycle</span>
  <p>The budget of 100 probes stops the loop, so the step cannot hang, and it writes no diagnostic of its own beyond the status: S07 makes exactly 100 probes and leaves a kit number that looks like any other. Cyclic replacement data is not hypothetical — it is what a double-entered or partially corrected extract looks like.</p>
  <p><strong>How the step handles it.</strong> After the loop the pointer is tested, not the loop index: <code>missing(kitnumrp)</code> is true exactly when the walk landed on a terminal record, so <code>UNRESOLVED</code> means the budget ran out. The 100 decides only how long a cyclic chain takes to give up — a real chain is three links at most, and S03 walks three — so the budget never decides an answer. The check asserts the status and the probe count of S07, which is what separates &ldquo;exhausted the budget&rdquo; from &ldquo;stopped early&rdquo; in the evidence rather than in the prose.</p>
</div>

<h3>5.4 The duplicate rule, and the deduplication in front of it</h3>
<p>Two questions live in the same two statements. The step already sorts the replacement rows with <code>nodupkey</code>, so is <code>duplicate: "error"</code> doing anything — and is the sorting the reason a load ever errors out? Neither, and the <code>by</code> list is where both are decided: it carries the hash key <em>plus</em> the hash payload, so the sort collapses exactly the rows that are identical on all five fields and nothing else. The two cases that separate the outcomes are S17 and S14.</p>
<table>
  <thead><tr><th style="width:120px;">Case</th><th>Rows entering the sort</th><th style="width:96px;">Keys reaching the load</th><th>Outcome</th></tr></thead>
  <tbody>
    <tr><td><span class="num">S17</span> — two rows agree</td>
        <td>3, of which two are byte-identical</td>
        <td><span class="num">2</span></td>
        <td>The identical pair is one event recorded twice and collapses. The load proceeds and the answer is <span class="num">1003 / LOT-C / B03</span>.</td></tr>
    <tr><td><span class="num">S14</span> — two rows disagree</td>
        <td>4, of which two claim the same kit with different successors</td>
        <td><span class="num">4</span></td>
        <td>The conflict survives the sort on purpose and the load refuses it: <code>ERROR: Duplicate key (101, 1002)</code>. The step stops and no output data set is produced.</td></tr>
  </tbody>
</table>
<p><strong>S14 is a data issue, not a defect in the step.</strong> Its two rows claim the same kit <span class="num">1002</span> with different lots and different successors. In the extract a kit carries its status, and a kit that was assigned was replaced at most once, so at most one of the two rows can describe what happened: the other is a duplicate or a stale row in the IRT extract. What the step owes a reader is to make that visible instead of choosing for them, and that is what the refusal does. The repair belongs upstream, in the extract.</p>
<p>So the sort neither raises the error nor suppresses the rule: it is what gives the rule something to catch. The declaration on its own would be inert, and the measurement is blunt about it — run the same four S14 rows through a <code>by</code> list of the key alone and they load as three keys, no duplicate ever reaches the load, and which of the two conflicting replacements wins is decided by the order the rows happen to arrive in: the same data then answers <span class="num">1003 / LOT-T3 / BT3</span> or <span class="num">1004 / LOT-T4 / BT4</span>. The model beside the check prints both answers from the same fixture.</p>

<div class="box note"><span class="t">What to protect</span>
  <p>The <code>by</code> list of the deduplication must contain the key <em>and</em> every payload field the hash carries. Add a field to <code>definedata</code> and the same field has to be added here, or a conflict on it becomes invisible again. A <code>by</code> list that already makes the key unique makes the declaration decorative — and the failure is silent, which is the whole reason this is written down.</p>
  <p>A conflict is a hard stop: the DATA step ends, no data set is produced, and the job fails. That severity is intended, because an unresolved conflict must not reach a submission. If the team would rather see the offending rows than fail, detect the conflict before the load, write it to a review data set, and there is then nothing left for <code>duplicate: "error"</code> to do. The check asserts the three row and key counts that decide whether the rule can fire at all; the refusal itself is one log line away, in the block §7.4 describes.</p>
</div>

<h3>5.5 What the step gets right</h3>
<ul>
  <li>Chain depth is genuinely open. Zero, one and three hops all resolve (S01, S02, S03), and the loop assumes nothing about how many links there are.</li>
  <li>The composite key is necessary, not decorative. S11 gives two subjects the same kit number with different replacements; a key on <code>kit_num</code> alone would have merged them.</li>
  <li>The physical order of the driving table does not matter. The visit-level feed is streamed in whatever order it arrives, and nothing has to be sorted by the lookup key.</li>
  <li>Case and one known alias are handled before the split, so the classification and the join back use the same label (S12).</li>
  <li>Every unresolved row carries both a status and a log line, and no resolved row carries either (S05, S06, S07, S10).</li>
</ul>

<div class="box takeaway"><span class="t">This section in one line</span><p>The step's job is the walk, and the walk is sound: the depth is open, the key is composite, order does not matter, and every unresolved row is labelled and counted. What it does not do is police the extract — the load's refusal is what makes a conflict visible, and the repair belongs upstream.</p></div>

<h3>5.6 Defects this step does not fix</h3>
<p>One finding is about the collapse rather than the walk. It is recorded here because it is the same class of failure — an answer that is well formed and wrong, with nothing in the log saying so.</p>

<div class="box finding"><span class="t">F4 &nbsp;one lot for several kits</span>
  <p>The collapse emits one row per subject and visit. <code>refid</code> lists every kit the visit resolved to, while <code>ECLOT</code> and <code>BATCHNUM</code> come from the single <code>last.vis_type</code> row, so a visit that ended on three kits reports one lot and one batch for all three. The check prints that record. The order inside the list is the sort key — kit type, then kit number — so it is grouped by kit type, not by the sequence in which the kits were administered.</p>
  <p>This is a specification question rather than a bug, but it is the kind that survives to a review table: a reviewer comparing <code>ECREFID</code> with <code>ECLOT</code> sees a one-to-many relationship that the specification may not have intended. Decide the cardinality, write it down, and if one identifier per kit is wanted, emit one row per kit instead of collapsing.</p>
  <p class="small">The accumulator is <code>length refid $200</code>. For five-digit kit numbers that holds 28 entries — <code>floor(202 / 7)</code> — and a visit carries a handful, so the cap is not reachable at these kit counts. It becomes reachable only if the cardinality above is changed to one number per kit for a visit with dozens of them, which is the same decision seen from the other side.</p>
</div>


<!-- ============================================================ -->
<h2><span class="n">6</span>Reuse checklist</h2>
<p class="lede">What to change, and what to check before the pattern goes into another program.</p>

<ul>
  <li><strong>Parameterise the input and the join key.</strong> The IRT table name, the subject variable and the visit variable are the only study-specific parts; keep them in one place.</li>
  <li><strong>Confirm the key types match.</strong> A numeric key on one side and a character key on the other gives a walk that probes with the wrong values and finds nothing — and a miss is a normal outcome of the loop, so this is the failure most likely to reach production unnoticed.</li>
  <li><strong>Decide the duplicate rule before the first run.</strong> If two rows can describe the same kit, encode the rule in a sort column, or use <code>duplicate: "error"</code> — and check that the deduplication upstream leaves the conflict in place for the load to see.</li>
  <li><strong>Keep a status column and count it.</strong> <code>chain_status</code> turns three log-only outcomes into something a QC step can fail on: a column is countable, log lines are not.</li>
  <li><strong>Drop the scratch variables.</strong> The hash payload and the pointer live in the PDV and are written out with everything else unless they are dropped deliberately.</li>
  <li><strong>Re-run the check after any change</strong> to the split, the key definition or the collapse. The expected values are cheap to maintain and the scenarios are the ones that actually break.</li>
</ul>


<!-- ============================================================ -->
<h2><span class="n">7</span>The check that ships with this note</h2>
<p class="lede">One self-contained SAS program, the dummy data behind every scenario, and what a passing run prints.</p>

<h3>7.1 The verifier</h3>
<p><a href="https://github.com/jinbeiwang/sas-pattern-notes/blob/main/kit_chain_check.sas"><code>kit_chain_check.sas</code></a> lives in its own repository, which also carries the fidelity check and the emulation named below. It is Base SAS only — no study macros, no formats, no external libraries, no input files: every row it reads is a <code>datalines</code> line or the output of a loop inside the program itself. It runs the four chain steps over one scenario at a time and asserts what came out. Five parts, in the order they appear:</p>
<ul>
  <li><strong>Fixture</strong> — one pipe-separated line per row of the IRT extract, for the twelve visit-level rows of §5.2. A <code>.</code> in the last field is a terminal kit.</li>
  <li><strong>Expected results</strong> — one line per visit-level row: the kit, lot, batch, status and probe count it must resolve to. These are the numbers printed in §5.2, and the fidelity check compares the two.</li>
  <li><strong>The step</strong> — Listings 1&ndash;4, run once per scenario through <code>%run_case</code>, plus the S14 precondition and the generated S15.</li>
  <li><strong>Comparison</strong> — expected against actual on case, subject and visit, five fields per row.</li>
  <li><strong>Regression gate</strong> — every assertion appends a row to <code>work.checks</code>; the log ends with the pass count and the process aborts if any line failed.</li>
</ul>
<p>The step it runs is the step in Listing&nbsp;1 to Listing&nbsp;4, and that is checked rather than claimed: <a href="https://github.com/jinbeiwang/sas-pattern-notes/blob/main/reference-model/code_fidelity.py"><code>reference-model/code_fidelity.py</code></a> compares the verifier's copy against the program statement by statement, ignoring comments, case and whitespace, and fails if a single statement is missing. The same script holds this note's listings to the program, and its matrix to the check's expected table. Two differences are expected and named in the file: the split reads the fixture instead of the study extract, and two lines count the probes each row makes, so the probe budget can be asserted rather than assumed.</p>

<h3>7.2 The dummy data, case by case</h3>
<p>The fixture as it stands in the program, read from the file rather than retyped. The field order is <code>case|rowid|scn_num|kit_num|lot_num|btch_num|vis_type|kit_tyds|kitnumrp</code>. Each case is run on its own, so kit numbers may repeat across scenarios, and the expected result of every line is the matching row of §5.2.</p>

<pre><code>S01|1|101|1001|LOT-A|B01|CYCLE 1 DAY 1|KIT|.
S02|1|101|1001|LOT-A|B01|CYCLE 1 DAY 1|KIT|1002
S02|2|101|1002|LOT-B|B02|KIT REPLACEMENT|KIT|.
S03|1|101|1001|LOT-A|B01|CYCLE 1 DAY 1|KIT|1002
S03|2|101|1002|LOT-B|B02|KIT REPLACEMENT|KIT|1003
S03|3|101|1003|LOT-C|B03|KIT REPLACEMENT|KIT|1004
S03|4|101|1004|LOT-D|B04|KIT REPLACEMENT|KIT|.
S05|1|101|1001|LOT-A|B01|CYCLE 1 DAY 1|KIT|9001
S05|2|101|1002|LOT-B|B02|KIT REPLACEMENT|KIT|.
S06|1|101|1001|LOT-A|B01|CYCLE 1 DAY 1|KIT|1002
S06|2|101|1002|LOT-B|B02|KIT REPLACEMENT|KIT|1099
S07|1|101|1001|LOT-A|B01|CYCLE 1 DAY 1|KIT|1002
S07|2|101|1002|LOT-B|B02|KIT REPLACEMENT|KIT|1003
S07|3|101|1003|LOT-C|B03|KIT REPLACEMENT|KIT|1002
S09|1|101|1001|LOT-A|B01|CYCLE 1 DAY 1|KIT|.
S09|2|101|1001|LOT-B|B02|KIT REPLACEMENT|KIT|1002
S10|1|101|1001|LOT-A|B01|CYCLE 1 DAY 1|KIT|1002
S11|1|101|1001|LOT-A|B01|CYCLE 1 DAY 1|KIT|1002
S11|2|101|1002|LOT-T1|BT1|KIT REPLACEMENT|KIT|.
S11|3|202|2001|LOT-X|B91|CYCLE 1 DAY 1|KIT|1002
S11|4|202|1002|LOT-T2|BT2|KIT REPLACEMENT|KIT|.
S12|1|101|1001|LOT-A|B01|discontinue|KIT|1002
S12|2|101|1002|LOT-B|B02|kit replacement|KIT|.
S14|1|101|1001|LOT-A|B01|CYCLE 1 DAY 1|KIT|1002
S14|2|101|1002|LOT-B1|B02|KIT REPLACEMENT|KIT|1003
S14|3|101|1002|LOT-B2|B03|KIT REPLACEMENT|KIT|1004
S14|4|101|1003|LOT-T3|BT3|KIT REPLACEMENT|KIT|.
S14|5|101|1004|LOT-T4|BT4|KIT REPLACEMENT|KIT|.
S17|1|101|1001|LOT-A|B01|CYCLE 1 DAY 1|KIT|1002
S17|2|101|1002|LOT-B|B02|KIT REPLACEMENT|KIT|1003
S17|3|101|1002|LOT-B|B02|KIT REPLACEMENT|KIT|1003
S17|4|101|1003|LOT-C|B03|KIT REPLACEMENT|KIT|.</code></pre>
<p class="small">S15 has no fixture line: it is generated, 2,000 subjects by four visits by default, each visit carrying its own block of kit numbers so that one visit's kits cannot collide with another's, and three replacement rows per visit. Its size is the macro parameter <code>vol_subjects</code> at the top of the file; set it to 0 to skip the case altogether. The F4 assertion builds its own three-row group, because it is about the collapse rather than the walk.</p>

<h3>7.3 What a passing run prints</h3>
<p>Three tables, all from data the program builds: the comparison, one row per fixture case with a verdict column; the F4 collapsed record; and the assertions, one line each — that last one is what to read after an edit. Besides the row-by-row comparison it covers the counts and the volume case:</p>
<table>
  <thead><tr><th style="width:96px;">Assertion</th><th>What it pins down</th></tr></thead>
  <tbody>
    <tr><td><span class="num">S14</span></td><td>Four replacement rows enter the deduplication and four keys leave it — the conflict is still there for the load. Under a <code>by</code> list of the key alone the same rows would leave three keys.</td></tr>
    <tr><td><span class="num">S17</span></td><td>Three replacement rows enter and two keys leave, under either <code>by</code> list: identical rows are still one event.</td></tr>
    <tr><td><span class="num">F4</span></td><td>The collapsed record for a three-kit visit: <code>ECREFID</code> lists all three numbers, while the kit, lot and batch columns are the last one's.</td></tr>
    <tr><td><span class="num">S15</span></td><td>8,000 visit rows were walked, all of them on the terminal kit, none of them over the probe budget.</td></tr>
  </tbody>
</table>
<p>Probes are asserted for every row, which is what distinguishes the two ways a walk can end: S07 must show exactly 100 probes and a status of <code>UNRESOLVED</code>, so a change that made the loop stop early would fail the check instead of looking like a fix.</p>

<h3>7.4 How to run it</h3>
<p>The file: <a href="https://github.com/jinbeiwang/sas-pattern-notes/blob/main/kit_chain_check.sas"><code>kit_chain_check.sas</code></a>, submitted as it stands.</p>

<pre><code>sas kit_chain_check.sas            <span class="cm"># batch: the log carries the report and the exit code</span>
                                   <span class="cm"># interactive: open the file and submit it</span></code></pre>
<p>A passing run ends the log with one line:</p>

<pre><code>kit chain check: 11 checks, 11 pass, 0 fail</code></pre>
<p class="small">11 is the number of rows the assertion table prints with the fixture as it stands, and the pass count has to equal it: one for the per-case comparison, three for each of the two duplicate cases, two for F4 and two for the volume case. A run that reports a smaller number has lost an assertion, not gained a pass.</p>
<p>Two things about the run are deliberate and are worth knowing before the log is read:</p>
<ul>
  <li><strong>The last block is expected to fail.</strong> S14 does not go through the loop with the others, because loading its conflict is supposed to stop the step. That block is the last thing in the file, it announces itself in the log, and it exists so the refusal is observed rather than cited. Set <code>demo_conflict = N</code> to skip it — which is also what to do where a scheduler treats an <code>ERROR</code> in the log as a failed job.</li>
  <li><strong>The volume case dominates the runtime.</strong> 24,000 replacement rows and 8,000 walked rows are nothing for SAS, but they are the slowest part of the check. Lower <code>vol_subjects</code> when volume is not the point being checked.</li>
</ul>
<p>After any edit to the program, two commands keep this note honest:</p>

<pre><code>python reference-model/code_fidelity.py   <span class="cm"># the listings, the fixture and the matrix, against the program</span>
python reference-model/ec_step_model.py   <span class="cm"># the same fixture through a dependency-free emulation</span></code></pre>

<h3>7.5 What it settles, and what it does not</h3>
<p>The check is code, not testimony: anything it asserts is settled by running it. Three behaviours are assumptions until then, and they are exactly what the run answers:</p>
<ol>
  <li>That a load declared <code>duplicate: "error"</code> ends the step with an error and produces no output data set, rather than warning and emitting a partial table. S14 rests on this.</li>
  <li>That a zero-row table can be loaded through the <code>dataset:</code> tag, which is how S10 reaches its dangling pointer.</li>
  <li>That the <code>while</code> test of <code>do i = 1 to 100 while (&hellip;)</code> is evaluated before the first iteration as well as before the rest, which is why S01 and S09 — rows whose pointer is already missing — must show zero probes.</li>
</ol>
<p>What it does not settle is whether the fixture covers the shapes the real IRT extract can take, which no program of this size can answer. The cases were chosen from the ways a replacement chain breaks — an absent kit, a cycle, a conflict, a duplicate, a volume case — and a new shape of bad input means a new fixture line, not a re-reading of this note.</p>
<hr>
<p class="small">The emulation in <a href="https://github.com/jinbeiwang/sas-pattern-notes/blob/main/reference-model/ec_step_model.py"><code>reference-model/ec_step_model.py</code></a> is not a second thing to maintain: it reads the fixture, the expected table and the volume parameters straight out of <code>kit_chain_check.sas</code>, so it cannot drift from it. It stays in the repository for the two things this environment cannot otherwise do: it runs without SAS, and it computes both deduplication counts and the answer each of them produces, which is the measurement behind §5.4.</p>

<footer>
  <p><strong>Verification</strong> The listings in §3 are the program as it stands, not a paraphrase of it, and that is checked rather than claimed: <code>reference-model/code_fidelity.py</code> compares every statement of the listings, and of the step that <code>kit_chain_check.sas</code> runs, against the program, and holds the fixture and the scenario matrix to it as well. The check is a single self-contained Base SAS program — twelve fixture cases, eleven assertions, no study macros and no external input — and the dummy data behind every case is printed in §7.2.</p>
  <p><strong>Not run</strong> SAS was not available in the environment where this note was written, so the expected results in §7 are the specification the check asserts rather than a log that was read; §7.5 lists the three behaviours that the run settles.</p>
  <p><strong>De-identification</strong> All data is synthetic: study identifiers are placeholders, no subject-level information is present, and the IRT extract is referred to by a generic name.</p>
</footer>
