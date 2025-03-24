const tableBoxes = document.querySelectorAll('.table-box');

function checkScrollbar(tableBox) {
  if (tableBox.scrollHeight > tableBox.clientHeight) {
    tableBox.style.paddingRight = '1rem';
  } else {
    tableBox.style.paddingRight = '0';
  }
}

const resizeObserver = new ResizeObserver(entries => {
  entries.forEach(entry => {
    checkScrollbar(entry.target);
  });
});

tableBoxes.forEach(tableBox => {
  checkScrollbar(tableBox);
  resizeObserver.observe(tableBox);
  setTimeout(() => {
    tableBox.style.transition = 'padding-right 0.3s ease';
  }, 200); // small delay to prevent transition on page load (cases shaking). But enables transition on sidebar movements, etc.
});