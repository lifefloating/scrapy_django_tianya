from django.shortcuts import render
from django.shortcuts import HttpResponse
from tianyadata import models
from django.views.generic import ListView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.

'''
def index(request):
    if request.method == "POST":
        pass
    # 数据库取出数据
    datalist = models.Index.objects.all().order_by('-story_replytime')

    return render(request, "index.html", {"datalist": datalist}) # context参数传递变量 datalist是指针
'''


class IndexView(ListView):
    model = models.Index  # 指定要获取的models
    template_name = "index.html"  # 指定这个视图渲染的模板
    context_object_name = "datalist"  # 指定获取的模型列表数据保存的变量名。这个变量会被传递给模板
    paginate_by = 50  # Listview已经实现Paginator类的分页逻辑 paginate_by指定每页显示数目 开启分页属性

    def get_queryset(self):
        return models.Index.objects.order_by('-story_replytime').all()

    def get_context_data(self, **kwargs):  # 传递模版变量给模版 相当于 render函数
        context = super().get_context_data(**kwargs)
        # 父类生成的字典中已有 paginator、page_obj、is_paginated 这三个模板变量，
        # paginator 是 Paginator 的一个实例，
        # page_obj 是 Page 的一个实例，
        # is_paginated 是一个布尔变量，用于指示是否已分页。
        # object_list 请求页面的对象列表 queryset 上面的datalist就是
        # 例如如果规定每页 10 个数据，而本身只有 5 个数据，其实就用不着分页，此时 is_paginated=False。
        # 由于 context 是一个字典，所以调用 get 方法从中取出某个键对应的值。
        paginator = context.get('paginator')
        page = context.get('page_obj')
        is_paginated = context.get('is_paginated')  # 布尔类型表示是否分页

        # 调用自己写的 pagination_data 方法获得显示分页导航条需要的数据
        pagination_data = self.pagination_data(paginator, page, is_paginated)

        # 将分页导航条的模板变量更新到 context字典 中，注意 pagination_data 方法返回的也是一个字典。
        context.update(pagination_data)

        # 将更新后的 context 返回，以便 ListView 使用这个字典中的模板变量去渲染模板。
        # 注意此时 context 字典中已有了显示分页导航条所需的数据。
        return context

    def pagination_data(self, paginator, page, is_paginated):
        if not is_paginated:  # 没有分页 返回一个空的字典
            return {}

        # 当前页左边连续的页码号，初始值为空
        left = []
        # 当前页右边连续的页码号，初始值为空
        right = []
        # 标示第 1 页页码后是否需要显示省略号
        left_has_more = False
        # 标示最后一页页码前是否需要显示省略号
        right_has_more = False

        # 标示是否需要显示第 1 页的页码号。
        # 因为如果当前页左边的连续页码号中已经含有第 1 页的页码号，此时就无需再显示第 1 页的页码号，
        # 其它情况下第一页的页码是始终需要显示的。
        # 初始值为 False
        first = False

        # 标示是否需要显示最后一页的页码号。
        last = False

        # 获得用户当前请求的页码号
        page_number = page.number

        # 获得分页后的总页数
        total_pages = paginator.num_pages

        # 获取分页页码列表
        page_range = paginator.page_range

        # 如果用户请求的是第一页的数据，那么当前页左边的不需要数据，因此 left=[]（已默认为空）。
        # 此时只要获取当前页右边的连续页码号，
        if page_number == 1:
            right = page_range[page_number:page_number + 3]
            # 如果最右边的页码号比最后一页的页码号减去 1 还要小，
            # 说明最右边的页码号和最后一页的页码号之间还有其它页码，因此需要显示省略号，通过 right_has_more 来指示。
            if right[-1] < total_pages - 1:
                right_has_more = True

            # 如果最右边的页码号比最后一页的页码号小，说明当前页右边的连续页码号中不包含最后一页的页码
            # 所以需要显示最后一页的页码号，通过 last 来指示
            if right[-1] < total_pages:
                last = True
        elif page_number == total_pages:
            # 如果用户请求的是最后一页的数据，那么当前页右边就不需要数据，因此 right=[]（已默认为空），
            # 此时只要获取当前页左边的连续页码号
            left = page_range[page_number - 4:page_number - 1]

            # 如果最左边的页码号比第 2 页页码号还大，
            # 说明最左边的页码号和第 1 页的页码号之间还有其它页码，因此需要显示省略号，通过 left_has_more 来指示
            if left[0] > 2:
                left_has_more = True
            # 如果最左边的页码号比第 1 页的页码号大，说明当前页左边的连续页码号中不包含第一页的页码，
            # 所以需要显示第一页的页码号，通过 first 来指示
            if left[0] > 1:
                first = True
        else:
            # 用户请求的既不是最后一页，也不是第 1 页，则需要获取当前页左右两边的连续页码号
            left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0:page_number - 1]
            right = page_range[page_number:page_number + 3]

            # 是否需要显示最后一页和最后一页前的省略号
            if right[-1] < total_pages - 1:
                right_has_more = True
            if right[-1] < total_pages:
                last = True

            # 是否需要显示第 1 页和第 1 页后的省略号
            if left[0] > 2:
                left_has_more = True
            if left[0] > 1:
                first = True

        data = {
            "left": left,
            "right": right,
            "left_has_more": left_has_more,
            "right_has_more": right_has_more,
            "first": first,
            "last": last,

        }

        return data


def detail(request):
    link = request.GET.get('link')
    link_cond = "-".join(link.split('-')[0:-1]).strip()
    storylist = models.Story.objects.filter(story_mark=link_cond).order_by('story_order').all()
    paginator = Paginator(storylist, 1)
    page = request.GET.get('page_detail')

    try:
        storys = paginator.page(page)
    except PageNotAnInteger:
        # 如果请求的页数不是整数，返回第一页。
        storys = paginator.page(1)
    except EmptyPage:
        # 如果请求的页数不在合法的页数范围内，返回结果的最后一页。
        storys = paginator.page(paginator.num_pages)

    return render(request, 'detail.html', {'storys': storys, 'link': link})
