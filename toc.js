// Populate the sidebar
//
// This is a script, and not included directly in the page, to control the total size of the book.
// The TOC contains an entry for each page, so if each page includes a copy of the TOC,
// the total size of the page becomes O(n**2).
class MDBookSidebarScrollbox extends HTMLElement {
    constructor() {
        super();
    }
    connectedCallback() {
        this.innerHTML = '<ol class="chapter"><li class="chapter-item expanded affix "><a href="index.html">PaCS-Toolkit User Guide</a></li><li class="chapter-item expanded "><a href="quickstart.html"><strong aria-hidden="true">1.</strong> Quick Start</a></li><li class="chapter-item expanded "><a href="install.html"><strong aria-hidden="true">2.</strong> Install</a></li><li class="chapter-item expanded "><a href="mdrun.html"><strong aria-hidden="true">3.</strong> mdrun</a></li><li><ol class="section"><li class="chapter-item expanded "><a href="mdrun/overview.html"><strong aria-hidden="true">3.1.</strong> Overview</a></li><li class="chapter-item expanded "><a href="mdrun/basic.html"><strong aria-hidden="true">3.2.</strong> Basic</a></li><li class="chapter-item expanded "><a href="mdrun/simulator.html"><strong aria-hidden="true">3.3.</strong> Simulator</a></li><li class="chapter-item expanded "><a href="mdrun/analyzer.html"><strong aria-hidden="true">3.4.</strong> Analyzer</a></li><li><ol class="section"><li class="chapter-item expanded "><a href="mdrun/analyzer/rmsd.html"><strong aria-hidden="true">3.4.1.</strong> rmsd</a></li><li class="chapter-item expanded "><a href="mdrun/analyzer/target.html"><strong aria-hidden="true">3.4.2.</strong> target</a></li><li class="chapter-item expanded "><a href="mdrun/analyzer/dissociation.html"><strong aria-hidden="true">3.4.3.</strong> dissociation</a></li><li class="chapter-item expanded "><a href="mdrun/analyzer/association.html"><strong aria-hidden="true">3.4.4.</strong> association</a></li><li class="chapter-item expanded "><a href="mdrun/analyzer/a_d.html"><strong aria-hidden="true">3.4.5.</strong> a_d</a></li><li class="chapter-item expanded "><a href="mdrun/analyzer/ee.html"><strong aria-hidden="true">3.4.6.</strong> ee</a></li><li class="chapter-item expanded "><a href="mdrun/analyzer/template.html"><strong aria-hidden="true">3.4.7.</strong> template</a></li></ol></li><li class="chapter-item expanded "><a href="mdrun/inputfile.html"><strong aria-hidden="true">3.5.</strong> Input file</a></li><li class="chapter-item expanded "><a href="mdrun/reference.html"><strong aria-hidden="true">3.6.</strong> Reference</a></li></ol></li><li class="chapter-item expanded "><a href="rmmol.html"><strong aria-hidden="true">4.</strong> rmmol</a></li><li class="chapter-item expanded "><a href="rmfile.html"><strong aria-hidden="true">5.</strong> rmfile</a></li><li class="chapter-item expanded "><a href="fit.html"><strong aria-hidden="true">6.</strong> fit</a></li><li class="chapter-item expanded "><a href="genrepresent.html"><strong aria-hidden="true">7.</strong> genrepresent</a></li><li class="chapter-item expanded "><a href="gencom.html"><strong aria-hidden="true">8.</strong> gencom</a></li><li class="chapter-item expanded "><a href="genfeature.html"><strong aria-hidden="true">9.</strong> genfeature</a></li><li><ol class="section"><li class="chapter-item expanded "><a href="genfeature/comdist.html"><strong aria-hidden="true">9.1.</strong> comdist</a></li><li class="chapter-item expanded "><a href="genfeature/comvec.html"><strong aria-hidden="true">9.2.</strong> comvec</a></li><li class="chapter-item expanded "><a href="genfeature/rmsd.html"><strong aria-hidden="true">9.3.</strong> rmsd</a></li><li class="chapter-item expanded "><a href="genfeature/xyz.html"><strong aria-hidden="true">9.4.</strong> xyz</a></li></ol></li><li class="chapter-item expanded "><a href="FAQ.html"><strong aria-hidden="true">10.</strong> FAQ</a></li></ol>';
        // Set the current, active page, and reveal it if it's hidden
        let current_page = document.location.href.toString().split("#")[0];
        if (current_page.endsWith("/")) {
            current_page += "index.html";
        }
        var links = Array.prototype.slice.call(this.querySelectorAll("a"));
        var l = links.length;
        for (var i = 0; i < l; ++i) {
            var link = links[i];
            var href = link.getAttribute("href");
            if (href && !href.startsWith("#") && !/^(?:[a-z+]+:)?\/\//.test(href)) {
                link.href = path_to_root + href;
            }
            // The "index" page is supposed to alias the first chapter in the book.
            if (link.href === current_page || (i === 0 && path_to_root === "" && current_page.endsWith("/index.html"))) {
                link.classList.add("active");
                var parent = link.parentElement;
                if (parent && parent.classList.contains("chapter-item")) {
                    parent.classList.add("expanded");
                }
                while (parent) {
                    if (parent.tagName === "LI" && parent.previousElementSibling) {
                        if (parent.previousElementSibling.classList.contains("chapter-item")) {
                            parent.previousElementSibling.classList.add("expanded");
                        }
                    }
                    parent = parent.parentElement;
                }
            }
        }
        // Track and set sidebar scroll position
        this.addEventListener('click', function(e) {
            if (e.target.tagName === 'A') {
                sessionStorage.setItem('sidebar-scroll', this.scrollTop);
            }
        }, { passive: true });
        var sidebarScrollTop = sessionStorage.getItem('sidebar-scroll');
        sessionStorage.removeItem('sidebar-scroll');
        if (sidebarScrollTop) {
            // preserve sidebar scroll position when navigating via links within sidebar
            this.scrollTop = sidebarScrollTop;
        } else {
            // scroll sidebar to current active section when navigating via "next/previous chapter" buttons
            var activeSection = document.querySelector('#sidebar .active');
            if (activeSection) {
                activeSection.scrollIntoView({ block: 'center' });
            }
        }
        // Toggle buttons
        var sidebarAnchorToggles = document.querySelectorAll('#sidebar a.toggle');
        function toggleSection(ev) {
            ev.currentTarget.parentElement.classList.toggle('expanded');
        }
        Array.from(sidebarAnchorToggles).forEach(function (el) {
            el.addEventListener('click', toggleSection);
        });
    }
}
window.customElements.define("mdbook-sidebar-scrollbox", MDBookSidebarScrollbox);
