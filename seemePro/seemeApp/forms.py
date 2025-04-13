from django import forms
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe

class ProfileAndPasswordForm(forms.ModelForm):
    # 密碼修改區塊，非必填
    old_password = forms.CharField(
        widget=forms.PasswordInput, 
        required=False, 
        label="目前密碼",
        help_text=mark_safe("<small style='color:red; display:block; margin-top:4px;'>若要修改密碼，請填寫目前密碼；否則可留空。</small>")
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput, 
        required=False, 
        label="新密碼"
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput, 
        required=False, 
        label="確認新密碼"
    )

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email"]
        labels = {
            'username': '用戶名',
            'first_name': '名字',
            'last_name': '姓氏',
            'email': '郵箱',
        }
        help_texts = {
            'username': mark_safe("<small style='color:red; display:block; margin-top:4px;'>必填。<br>150個字符以內，只允許字母、數字及 @/./+/-/_ 等符號。</small>"),
        }

    def clean(self):
        cleaned_data = super().clean()
        old_password = cleaned_data.get("old_password")
        new_password1 = cleaned_data.get("new_password1")
        new_password2 = cleaned_data.get("new_password2")
        # 如果任何一個密碼欄位有填，則三個必須都有填寫
        if old_password or new_password1 or new_password2:
            if not old_password:
                self.add_error("old_password", "請輸入目前密碼以進行修改。")
            if not new_password1:
                self.add_error("new_password1", "請輸入新密碼。")
            if not new_password2:
                self.add_error("new_password2", "請確認新密碼。")
            if new_password1 and new_password2 and new_password1 != new_password2:
                self.add_error("new_password2", "新密碼不匹配。")
        return cleaned_data