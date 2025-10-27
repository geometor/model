// Custom navigation logic for the Sphinxilator theme

window.addEventListener('DOMContentLoaded', (event) => {
    // --- Mobile Nav Toggle ---
    const mobileNavToggle = document.querySelector('[data-toggle="wy-nav-top"]');
    const mainNav = document.querySelector('[data-toggle="wy-nav-shift"]');
    
    if (mobileNavToggle && mainNav) {
        mobileNavToggle.addEventListener('click', () => {
            mainNav.classList.toggle('shift');
        });
    }

    // --- Sidebar Menu Expansion ---
    const menuItems = document.querySelectorAll('.wy-menu-vertical a');

    menuItems.forEach(menuItem => {
        const expandButton = menuItem.querySelector('.toctree-expand');
        if (expandButton) {
            expandButton.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                
                const parentLi = menuItem.closest('li');
                parentLi.classList.toggle('current');

                // Also collapse other open menus at the same level
                const siblings = parentLi.parentElement.children;
                for (let sibling of siblings) {
                    if (sibling !== parentLi && sibling.classList.contains('current')) {
                        sibling.classList.remove('current');
                    }
                }
            });
        }
    });
});
