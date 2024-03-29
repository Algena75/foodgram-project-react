from django.urls import include, path
from recipes.views import IngredientViewSet, RecipeViewSet, TagViewSet
from rest_framework.routers import DefaultRouter
from users.views import UserViewSet

app_name = 'api'

router_v1 = DefaultRouter()

router_v1.register(
    r'tags',
    TagViewSet,
    basename='tag'
)

router_v1.register(
    r'ingredients',
    IngredientViewSet,
    basename='ingredient'
)
router_v1.register(
    r'recipes',
    RecipeViewSet,
    basename='recipe'
)
router_v1.register('users', UserViewSet, basename='user')


urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
