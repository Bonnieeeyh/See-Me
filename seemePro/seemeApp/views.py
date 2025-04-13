# seemeApp/views.py

import os
import json
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from django.contrib.auth import login, logout, authenticate
from .models import TestResult
from django.contrib.auth import update_session_auth_hash
from .forms import ProfileAndPasswordForm

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "註冊成功，已登入！")
            return redirect("test_form")
        else:
            messages.error(request, "註冊失敗，請檢查資料。")
    else:
        form = UserCreationForm()
    return render(request, "seemeApp/register.html", {"form": form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # 获取用户名和密码进行认证
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "登录成功！")
                return redirect("profile")
            else:
                messages.error(request, "使用者名稱或密碼不正確。")
        else:
            messages.error(request, "登入失敗，請檢查資料。")
    else:
        form = AuthenticationForm()
    return render(request, "seemeApp/login.html", {"form": form})

def logout_view(request):
    logout(request)
    messages.info(request, "已登出。")
    return redirect("login")

@login_required
def test_form(request):
    config_path = os.path.join(settings.BASE_DIR, "seemeApp", "config", "question_config.json")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except Exception as e:
        return render(request, "seemeApp/error.html", {"error": f"加载配置文件出错: {e}"})
    
    questions = config.get("questions", [])
    score_options = [1, 2, 3, 4, 5]
    dimension_mapping = config.get("dimension_mapping", {})

    if request.method == "POST":
        responses = {}
        for q in questions:
            qid = str(q["id"])
            answer = request.POST.get(f"question_{qid}")
            if answer is None:
                messages.error(request, f"題目 {qid} 未作答，請完成所有題目。")
                return redirect("test_form")
            responses[qid] = int(answer)
        
        # 計算每個維度的總分和題目數量
        dimension_scores = {}
        dimension_counts = {}
        for qid, score in responses.items():
            dimension = dimension_mapping.get(qid, "未知")
            dimension_scores[dimension] = dimension_scores.get(dimension, 0) + score
            dimension_counts[dimension] = dimension_counts.get(dimension, 0) + 1

        # 計算每個維度的平均分
        dimension_averages = {d: dimension_scores[d] / dimension_counts[d] for d in dimension_scores}

        # 儲存或更新測驗結果 (方案一：存入 dimension_counts)
        try:
            test_result = TestResult.objects.get(user=request.user)
        except TestResult.DoesNotExist:
            test_result = TestResult(user=request.user)
        test_result.raw_answers = responses
        test_result.dimension_scores = dimension_scores
        test_result.dimension_averages = dimension_averages
        test_result.dimension_counts = dimension_counts  # 將題目數量存入
        test_result.save()

        context = {
            "responses": responses,
            "dimension_scores": dimension_scores,
            "dimension_counts": dimension_counts,
            "dimension_averages": dimension_averages,
        }
        return render(request, "seemeApp/result.html", context)
    else:
        return render(request, "seemeApp/test_form.html", {"questions": questions, "score_options": score_options})

@login_required
def profile_view(request):
    user = request.user
    try:
        test_result = TestResult.objects.get(user=user)
    except TestResult.DoesNotExist:
        test_result = None
    return render(request, "seemeApp/profile.html", {"user": user, "test_result": test_result})


@login_required
def profile_edit(request):
    if request.method == "POST":
        form = ProfileAndPasswordForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)  # 保存基本資料，但不立即提交
            old_password = form.cleaned_data.get("old_password")
            new_password1 = form.cleaned_data.get("new_password1")
            # 如果密碼修改區塊有填，則先驗證目前密碼
            if old_password or new_password1:
                if not request.user.check_password(old_password):
                    form.add_error("old_password", "目前密碼不正確。")
                    return render(request, "seemeApp/profile_edit.html", {"form": form})
                user.set_password(new_password1)
            user.save()
            update_session_auth_hash(request, user)  # 修改密碼後保持登入狀態
            messages.success(request, "個人資料及密碼已更新。")
            return redirect("profile")
        else:
            messages.error(request, "更新失敗，請檢查資料。")
    else:
        form = ProfileAndPasswordForm(instance=request.user)
    return render(request, "seemeApp/profile_edit.html", {"form": form})


@login_required
def report_detail(request):
    try:
        test_result = TestResult.objects.get(user=request.user)
    except TestResult.DoesNotExist:
        messages.error(request, "您尚未進行測驗，無法查看報告。")
        return redirect("test_form")

    # 注意：將 dimension_counts 一併放入 context
    context = {
        "responses": test_result.raw_answers,
        "dimension_scores": test_result.dimension_scores,
        "dimension_averages": test_result.dimension_averages,
        "dimension_counts": test_result.dimension_counts,
    }
    return render(request, "seemeApp/result.html", context)
