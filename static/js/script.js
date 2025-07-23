// All-in-one script for PrintReady: auth, file handling, rendering

document.addEventListener('DOMContentLoaded', () => {
  const defaultUsers = {
    'student@mits.ac.in': { password: '123', role: 'student', name: 'Default Student' },
    'staff@mits.ac.in': { password: '123', role: 'staff', name: 'Default Staff' }
  };
  let users = JSON.parse(localStorage.getItem('printUsers')) || defaultUsers;
  let printJobs = JSON.parse(localStorage.getItem('printJobs')) || [];
  let currentUser = JSON.parse(sessionStorage.getItem('currentUser')) || null;
  let selectedFile = null, jobIdToUpdate = null;

  const save = (key, val) => localStorage.setItem(key, JSON.stringify(val));
  const saveSession = () => sessionStorage.setItem('currentUser', JSON.stringify(currentUser));
  const clearSession = () => sessionStorage.removeItem('currentUser');
  const getStatusClass = s => ({
    Queued: 'bg-yellow-100 text-yellow-800',
    Printing: 'bg-blue-100 text-blue-800',
    'Ready for Pickup': 'bg-green-100 text-green-800',
    Completed: 'bg-gray-200 text-gray-800'
  }[s] || 'bg-gray-100 text-gray-800');

  const showModal = id => { jobIdToUpdate = id; document.getElementById('status-modal')?.classList.remove('hidden'); };
  const hideModal = () => { jobIdToUpdate = null; document.getElementById('status-modal')?.classList.add('hidden'); };

  const renderStudentJobs = () => {
    const list = document.getElementById('student-jobs-list'), msg = document.getElementById('student-no-jobs');
    if (!list || !msg) return;
    const jobs = printJobs.filter(j => j.userEmail === currentUser.email).sort((a, b) => new Date(b.submittedAt) - new Date(a.submittedAt));
    list.innerHTML = jobs.map(j => `
      <tr class="hover:bg-gray-50">
        <td class="px-6 py-4 text-sm font-medium text-gray-900">${j.filename}</td>
        <td class="px-6 py-4 text-sm text-gray-500">${new Date(j.submittedAt).toLocaleString()}</td>
        <td class="px-6 py-4 text-sm text-gray-500">
          <span class="px-2 inline-flex text-xs font-semibold rounded-full ${getStatusClass(j.status)}">${j.status}</span>
        </td>
      </tr>`).join('');
    msg.classList.toggle('hidden', jobs.length > 0);
  };

  const renderStaffJobs = () => {
    const active = document.getElementById('staff-active-jobs-list');
    const completed = document.getElementById('staff-completed-jobs-list');
    const noAct = document.getElementById('staff-no-active-jobs');
    const noComp = document.getElementById('staff-no-completed-jobs');
    if (!active || !completed) return;
    const act = printJobs.filter(j => j.status !== 'Completed');
    const comp = printJobs.filter(j => j.status === 'Completed');

    active.innerHTML = act.map(j => `
      <tr class="hover:bg-gray-50">
        <td class="px-6 py-4 text-sm font-medium text-gray-900">${j.filename}</td>
        <td class="px-6 py-4 text-sm text-gray-500">${j.userEmail}</td>
        <td class="px-6 py-4 text-sm text-gray-500">${j.copies}x, ${j.printType}</td>
        <td class="px-6 py-4 text-sm text-gray-500">${new Date(j.submittedAt).toLocaleString()}</td>
        <td class="px-6 py-4"><span class="px-2 inline-flex text-xs font-semibold rounded-full ${getStatusClass(j.status)}">${j.status}</span></td>
        <td class="px-6 py-4 text-sm font-medium space-x-2">
          <button class="text-blue-600 update-status-btn" data-id="${j.id}">Update</button>
          <a href="#" class="text-blue-600">Download</a>
        </td>
      </tr>`).join('');

    completed.innerHTML = comp.map(j => `
      <tr class="hover:bg-gray-50">
        <td class="px-6 py-4 text-sm font-medium text-gray-900">${j.filename}</td>
        <td class="px-6 py-4 text-sm text-gray-500">${j.userEmail}</td>
        <td class="px-6 py-4 text-sm text-gray-500">${new Date(j.completedAt).toLocaleString()}</td>
        <td class="px-6 py-4 text-sm text-gray-500">${j.completedBy}</td>
      </tr>`).join('');

    [noAct, noComp].forEach((el, i) => el?.classList.toggle('hidden', (i ? comp : act).length > 0));
    document.querySelectorAll('.update-status-btn').forEach(btn => btn.onclick = () => showModal(+btn.dataset.id));
  };

  const handleLogin = e => {
    e.preventDefault();
    const { email, password } = e.target;
    const user = users[email.value];
    const err = document.getElementById('login-error');
    if (user && user.password === password.value) {
      currentUser = { email: email.value, role: user.role, name: user.name };
      saveSession();
      location.href = user.role === 'student' ? 'student.html' : 'staff.html';
    } else err.classList.remove('hidden');
  };

  const handleSignup = e => {
    e.preventDefault();
    const email = document.getElementById('signup-email').value;
    const err = document.getElementById('signup-error');
    if (users[email]) return err.textContent = 'Email exists.', err.classList.remove('hidden');
    users[email] = {
      name: document.getElementById('name').value,
      mutId: document.getElementById('mut-id').value,
      batch: document.getElementById('batch').value,
      password: document.getElementById('signup-password').value,
      role: 'student'
    };
    save('printUsers', users);
    location.href = 'login.html';
  };

  const handleLogout = () => { clearSession(); location.href = 'login.html'; };

  const handleFileUpload = e => {
    e.preventDefault();
    const status = document.getElementById('upload-status');
    if (!selectedFile) return status.textContent = 'Please select a file.', status.className = 'mt-2 text-sm text-red-500';
    const job = {
      id: Date.now(),
      userEmail: currentUser.email,
      filename: selectedFile.name,
      copies: document.getElementById('copies').value,
      printType: document.getElementById('print-type').value,
      status: 'Queued',
      submittedAt: new Date().toISOString()
    };
    printJobs.push(job);
    save('printJobs', printJobs);
    renderStudentJobs();
    status.textContent = '✅ Job submitted!';
    status.className = 'mt-2 text-sm text-green-600';
    document.getElementById('upload-form').reset();
    document.getElementById('file-name-display').textContent = '';
    selectedFile = null;
    setTimeout(() => { status.textContent = ''; }, 3000);
  };

  const handleStatusUpdate = () => {
    const status = document.getElementById('modal-status-select').value;
    const job = printJobs.find(j => j.id === jobIdToUpdate);
    if (job) {
      job.status = status;
      if (status === 'Completed') {
        job.completedBy = currentUser.email;
        job.completedAt = new Date().toISOString();
      }
      save('printJobs', printJobs);
      renderStaffJobs();
    }
    hideModal();
  };

  const init = () => {
    lucide.createIcons();
    const page = location.pathname.split('/').pop();
    if (['login.html', ''].includes(page)) {
      if (currentUser) return location.href = currentUser.role === 'student' ? 'student.html' : 'staff.html';
      document.getElementById('login-form')?.addEventListener('submit', handleLogin);
    } else if (page === 'signup.html') {
      document.getElementById('signup-form')?.addEventListener('submit', handleSignup);
    } else {
      if (!currentUser) return location.href = 'login.html';
      document.getElementById('user-email').textContent = currentUser.email;
      document.getElementById('logout-btn')?.addEventListener('click', handleLogout);
      if (page === 'student.html') {
        if (currentUser.role !== 'student') return handleLogout();
        const form = document.getElementById('upload-form');
        const drop = document.getElementById('drop-zone');
        const input = document.getElementById('file-upload');
        const name = document.getElementById('file-name-display');
        form?.addEventListener('submit', handleFileUpload);
        drop?.addEventListener('click', () => input.click());
        drop?.addEventListener('dragover', e => { e.preventDefault(); drop.classList.add('bg-blue-50', 'border-blue-500'); });
        drop?.addEventListener('dragleave', () => drop.classList.remove('bg-blue-50', 'border-blue-500'));
        drop?.addEventListener('drop', e => {
          e.preventDefault();
          drop.classList.remove('bg-blue-50', 'border-blue-500');
          if (e.dataTransfer.files.length) {
            input.files = e.dataTransfer.files;
            selectedFile = input.files[0];
            name.textContent = `Selected: ${selectedFile.name}`;
          }
        });
        input?.addEventListener('change', () => {
          if (input.files.length) {
            selectedFile = input.files[0];
            name.textContent = `Selected: ${selectedFile.name}`;
          }
        });
        renderStudentJobs();
      }
      if (page === 'staff.html') {
        if (currentUser.role !== 'staff') return handleLogout();
        const tab1 = document.getElementById('tab-active-queue');
        const tab2 = document.getElementById('tab-completed-history');
        const con1 = document.getElementById('content-active-queue');
        const con2 = document.getElementById('content-completed-history');
        tab1?.addEventListener('click', () => {
          con1.classList.remove('hidden'); con2.classList.add('hidden');
          tab1.className = tab1.className.replace(/text-gray.+/, 'text-blue-600 border-blue-500');
          tab2.className = tab2.className.replace(/text-blue.+/, 'text-gray-500 hover:text-gray-700 hover:border-gray-300');
        });
        tab2?.addEventListener('click', () => {
          con2.classList.remove('hidden'); con1.classList.add('hidden');
          tab2.className = tab2.className.replace(/text-gray.+/, 'text-blue-600 border-blue-500');
          tab1.className = tab1.className.replace(/text-blue.+/, 'text-gray-500 hover:text-gray-700 hover:border-gray-300');
        });
        document.getElementById('modal-confirm-btn')?.addEventListener('click', handleStatusUpdate);
        document.getElementById('modal-cancel-btn')?.addEventListener('click', hideModal);
        renderStaffJobs();
      }
    }
  };

  init();
});
