/* Anti-copy protection — disable right-click, Ctrl+C, Ctrl+A, Ctrl+S, F12 */
(function(){
    document.addEventListener('contextmenu', function(e){ e.preventDefault(); return false; });
    document.addEventListener('keydown', function(e){
        if (e.ctrlKey && (e.key === 'c' || e.key === 'C' || e.key === 'a' || e.key === 'A' || e.key === 's' || e.key === 'S' || e.key === 'u' || e.key === 'U')) {
            e.preventDefault(); return false;
        }
        if (e.key === 'F12') { e.preventDefault(); return false; }
    });
    document.addEventListener('selectstart', function(e){ e.preventDefault(); return false; });
    document.addEventListener('dragstart', function(e){ e.preventDefault(); return false; });

    /* Scroll to hash fragment + highlight after page load.
       Large pages (29MB+) may not finish parsing before browser
       gives up on native #fragment scrolling. Poll until target exists. */
    if (window.location.hash) {
        var targetId = window.location.hash.substring(1);
        var attempts = 0;
        var maxAttempts = 50;
        var scrolled = false;
        function tryScroll() {
            var el = document.getElementById(targetId);
            if (el) {
                if (!scrolled) {
                    el.scrollIntoView({ block: 'start' });
                    scrolled = true;
                }
                // Flash highlight on the target paragraph
                el.style.animation = 'para-flash 10s ease-out';
                el.classList.add('para-highlight');
                setTimeout(function(){ el.classList.remove('para-highlight'); el.style.animation = ''; }, 10000);
                return;
            }
            if (++attempts < maxAttempts) {
                setTimeout(tryScroll, 150);
            }
        }
        tryScroll();
        document.addEventListener('DOMContentLoaded', tryScroll);
        window.addEventListener('load', tryScroll);
    }
})();
