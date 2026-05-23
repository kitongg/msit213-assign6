from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import views as auth_views
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from .models import Album, Photo
from .forms import AlbumForm, PhotoForm, RegisterForm, UsernamePasswordResetForm, SimplePasswordChangeForm

User = get_user_model()
from django.views.generic.edit import FormView
from django.contrib.auth import logout
from django.shortcuts import redirect


def logout_and_redirect(request):
    """Log out the user and redirect to home page immediately."""
    logout(request)
    return redirect('/')


class RegisterView(FormView):
    template_name = 'registration/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class CustomPasswordResetView(auth_views.PasswordResetView):
    """
    Two-step inline reset: first enter username, then set new password on same page.
    This bypasses email sending in dev and allows immediate password change.
    """
    form_class = UsernamePasswordResetForm
    template_name = 'registration/password_reset_form.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return self.render_to_response({'form': form, 'stage': 'enter_username'})

    def post(self, request, *args, **kwargs):
        data = request.POST
        # Stage 1: submitted username only
        if 'username' in data and 'new_password1' not in data:
            form = self.form_class(data)
            if form.is_valid():
                username = form.cleaned_data['username']
                users = list(User._default_manager.filter(username__iexact=username, is_active=True))
                if not users:
                    form.add_error('username', 'No active user with that username')
                    return self.render_to_response({'form': form, 'stage': 'enter_username'})
                # proceed to stage 2
                from .forms import SimpleSetPasswordForm
                set_form = SimpleSetPasswordForm()
                return self.render_to_response({'form': set_form, 'stage': 'set_password', 'username': username})
            return self.render_to_response({'form': form, 'stage': 'enter_username'})

        # Stage 2: submitted new passwords
        if 'new_password1' in data:
            from .forms import SimpleSetPasswordForm
            set_form = SimpleSetPasswordForm(data)
            username = data.get('username')
            if not username:
                set_form.add_error(None, 'Missing username')
                return self.render_to_response({'form': set_form, 'stage': 'set_password'})
            users = list(User._default_manager.filter(username__iexact=username, is_active=True))
            if not users:
                set_form.add_error(None, 'Invalid username')
                return self.render_to_response({'form': set_form, 'stage': 'set_password'})
            user = users[0]
            if set_form.is_valid():
                new_pass = set_form.cleaned_data['new_password1']
                user.set_password(new_pass)
                user.save()
                # render success on same page
                return self.render_to_response({'form': set_form, 'stage': 'success'})
            return self.render_to_response({'form': set_form, 'stage': 'set_password', 'username': username})

        # fallback
        form = self.form_class()
        return self.render_to_response({'form': form, 'stage': 'enter_username'})


class CustomPasswordChangeView(auth_views.PasswordChangeView):
    form_class = SimplePasswordChangeForm
    template_name = 'registration/password_change_form.html'
    success_url = reverse_lazy('password_change')

    def form_valid(self, form):
        form.save()
        context = self.get_context_data(form=form, success=True)
        return self.render_to_response(context)


class AlbumAdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

class AlbumListView(ListView):
    model = Album
    template_name = 'album_list.html'
    context_object_name = 'albums'

class AlbumDetailView(DetailView):
    model = Album
    template_name = 'album_detail.html'
    context_object_name = 'album'

class AlbumCreateView(LoginRequiredMixin, CreateView):
    model = Album
    form_class = AlbumForm
    template_name = 'album_form.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class AlbumUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Album
    form_class = AlbumForm
    template_name = 'album_form.html'

    def test_func(self):
        album = self.get_object()
        return self.request.user == album.owner or self.request.user.is_staff

class AlbumDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Album
    template_name = 'album_confirm_delete.html'
    success_url = reverse_lazy('albums:album-list')

    def test_func(self):
        album = self.get_object()
        return self.request.user == album.owner or self.request.user.is_staff

class PhotoCreateView(LoginRequiredMixin, CreateView):
    model = Photo
    form_class = PhotoForm
    template_name = 'photo_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.album = Album.objects.get(pk=kwargs['album_pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.album = self.album
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('albums:album-detail', args=[self.album.pk])

class PhotoUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Photo
    form_class = PhotoForm
    template_name = 'photo_form.html'

    def test_func(self):
        photo = self.get_object()
        return self.request.user == photo.album.owner or self.request.user.is_staff

    def get_success_url(self):
        return reverse('albums:album-detail', args=[self.object.album.pk])

class PhotoDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Photo
    template_name = 'photo_confirm_delete.html'

    def test_func(self):
        photo = self.get_object()
        return self.request.user == photo.album.owner or self.request.user.is_staff

    def get_success_url(self):
        return reverse('albums:album-detail', args=[self.get_object().album.pk])
